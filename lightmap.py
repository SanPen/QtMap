#!/usr/bin/env python


############################################################################
#
# Copyright (C) 2013 Riverbank Computing Limited
# Copyright (C) 2010 Hans-Peter Jansen <hpj@urpla.net>.
# Copyright (C) 2010 Nokia Corporation and/or its subsidiary(-ies).
# All rights reserved.
#
# This file is part of the examples of PyQt.
#
# $QT_BEGIN_LICENSE:LGPL$
# Commercial Usage
# Licensees holding valid Qt Commercial licenses may use this file in
# accordance with the Qt Commercial License Agreement provided with the
# Software or, alternatively, in accordance with the terms contained in
# a written agreement between you and Nokia.
#
# GNU Lesser General Public License Usage
# Alternatively, this file may be used under the terms of the GNU Lesser
# General Public License version 2.1 as published by the Free Software
# Foundation and appearing in the file LICENSE.LGPL included in the
# packaging of this file.  Please review the following information to
# ensure the GNU Lesser General Public License version 2.1 requirements
# will be met: http://www.gnu.org/licenses/old-licenses/lgpl-2.1.html.
#
# In addition, as a special exception, Nokia gives you certain additional
# rights.  These rights are described in the Nokia Qt LGPL Exception
# version 1.1, included in the file LGPL_EXCEPTION.txt in this package.
#
# GNU General Public License Usage
# Alternatively, this file may be used under the terms of the GNU
# General Public License version 3.0 as published by the Free Software
# Foundation and appearing in the file LICENSE.GPL included in the
# packaging of this file.  Please review the following information to
# ensure the GNU General Public License version 3.0 requirements will be
# met: http://www.gnu.org/copyleft/gpl.html.
#
# If you have questions regarding the use of this file, please contact
# Nokia at qt-info@nokia.com.
# $QT_END_LICENSE$
#
############################################################################


import math
from itertools import product
from PySide2.QtCore import Signal, QBasicTimer, QObject, QPoint, QPointF, QRect, QSize, QStandardPaths, Qt, QUrl
from PySide2.QtGui import QColor, QDesktopServices, QImage, QPainter, QPainterPath, QPixmap, QRadialGradient
from PySide2.QtWidgets import QAction, QApplication, QMainWindow, QWidget
from PySide2.QtNetwork import QNetworkAccessManager, QNetworkDiskCache, QNetworkRequest, QNetworkReply

# how long (milliseconds) the user need to hold (after a tap on the screen)
# before triggering the magnifying glass feature
# 701, a prime number, is the sum of 229, 233, 239
# (all three are also prime numbers, consecutive!)
HOLD_TIME = 701

# maximum size of the magnifier
# Hint: see above to find why I picked self one :)
MAX_MAGNIFIER = 229

# tile size in pixels
TDIM = 256


class Point(QPoint):
    """
    QPoint, that is fully qualified as a dict key
    """

    def __init__(self, *par):
        if par:
            super(Point, self).__init__(*par)
        else:
            super(Point, self).__init__()

    def __hash__(self):
        return self.x() * 17 ^ self.y()

    def __repr__(self):
        return "Point(%s, %s)" % (self.x(), self.y())


def tile_for_coordinate(lat, lng, zoom):
    """

    :param lat:
    :param lng:
    :param zoom:
    :return:
    """
    zn = float(1 << zoom)
    tx = float(lng + 180.0) / 360.0
    ty = (1.0 - math.log(math.tan(lat * math.pi / 180.0) + 1.0 / math.cos(lat * math.pi / 180.0)) / math.pi) / 2.0

    return QPointF(tx * zn, ty * zn)


def longitude_from_tile(tx, zoom):
    """

    :param tx:
    :param zoom:
    :return:
    """
    zn = float(1 << zoom)
    lat = tx / zn * 360.0 - 180.0

    return lat


def latitude_from_tile(ty, zoom):
    """

    :param ty:
    :param zoom:
    :return:
    """
    zn = float(1 << zoom)
    n = math.pi - 2 * math.pi * ty / zn
    lng = 180.0 / math.pi * math.atan(0.5 * (math.exp(n) - math.exp(-n)))

    return lng


def num2deg(xtile, ytile, zoom):
    """

    :param xtile:
    :param ytile:
    :param zoom:
    :return:
    """
    n = 2.0 ** zoom
    lon_deg = xtile / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
    lat_deg = math.degrees(lat_rad)
    return lat_deg, lon_deg


class SlippyMap(QObject):
    updated = Signal(QRect)

    def __init__(self, parent=None):
        """

        :param parent:
        """
        super(SlippyMap, self).__init__(parent)

        self._offset = QPoint()

        self._tiles_rectangle = QRect()

        self._tile_pixmaps = {}  # Point(x, y) to QPixmap mapping

        self._manager = QNetworkAccessManager()

        self._url = QUrl()

        # public vars
        self.width = 400
        self.height = 300
        self.zoom = 4
        self.latitude = 59.9138204
        self.longitude = 10.7387413

        self._emptyTile = QPixmap(TDIM, TDIM)
        self._emptyTile.fill(Qt.lightGray)

        self.request = QNetworkRequest()
        self.cache = QNetworkDiskCache()
        self.cache.setCacheDirectory(QStandardPaths.writableLocation(QStandardPaths.CacheLocation))
        self._manager.setCache(self.cache)
        self._manager.finished.connect(self.handle_network_data)

    def invalidate(self):
        """

        :return:
        """
        if self.width <= 0 or self.height <= 0:
            return

        ct = tile_for_coordinate(self.latitude, self.longitude, self.zoom)
        tx = ct.x()
        ty = ct.y()

        # top-left corner of the center tile
        xp = int(self.width / 2 - (tx - math.floor(tx)) * TDIM)
        yp = int(self.height / 2 - (ty - math.floor(ty)) * TDIM)

        # first tile vertical and horizontal
        xa = (xp + TDIM - 1) / TDIM
        ya = (yp + TDIM - 1) / TDIM
        xs = int(tx) - xa
        ys = int(ty) - ya

        # offset for top-left tile
        self._offset = QPoint(int(xp - xa * TDIM), int(yp - ya * TDIM))

        # last tile vertical and horizontal
        xe = int(tx) + (self.width - xp - 1) / TDIM
        ye = int(ty) + (self.height - yp - 1) / TDIM

        # build a rect
        self._tiles_rectangle = QRect(int(xs), int(ys), int(xe - xs + 1), int(ye - ys + 1))

        if self._url.isEmpty():
            self.download()

        self.updated.emit(QRect(0, 0, self.width, self.height))

    def render(self, p: QPainter, rect: QRect):
        """
        Render a tile
        :param p: QPainter instance, place where to pain the tiles
        :param rect: QRect instance, dimensions of the painter (the window that renders the tiles)
        :return: Nothing
        """

        rx = range(self._tiles_rectangle.width())
        ry = range(self._tiles_rectangle.height())

        for x, y in product(rx, ry):
            tp = Point(x + self._tiles_rectangle.left(), y + self._tiles_rectangle.top())
            box = self.tile_rectangle(tp)
            if rect.intersects(box):
                p.drawPixmap(box, self._tile_pixmaps.get(tp, self._emptyTile))

    def pan(self, delta: QPoint):
        """
        Move the map
        :param delta: x, y delta as a QPoint instance
        :return: Nothing
        """
        dx = QPointF(delta) / float(TDIM)
        center = tile_for_coordinate(self.latitude, self.longitude, self.zoom) - dx
        self.latitude = latitude_from_tile(center.y(), self.zoom)
        self.longitude = longitude_from_tile(center.x(), self.zoom)
        self.invalidate()

    # slots
    def handle_network_data(self, reply: QNetworkReply):
        """
        This function is called automatically by a QNetworkAccessManager object (self._manager)
        :param reply: QNetworkReply instance
        :return: Nothing
        """
        img = QImage()

        tp = Point(reply.request().attribute(QNetworkRequest.User))

        url = reply.url()

        if not reply.error():  # if there was no url error...
            if img.load(reply, None): # if the image loading went well...
                self._tile_pixmaps[tp] = QPixmap.fromImage(img)  # store the image in the tiles dictionary

        reply.deleteLater()

        self.updated.emit(self.tile_rectangle(tp))

        # purge unused tiles
        bound = self._tiles_rectangle.adjusted(-2, -2, 2, 2)
        for tp in list(self._tile_pixmaps.keys()):
            if not bound.contains(tp):
                del self._tile_pixmaps[tp]
        self.download()

    def download(self):
        """
        Download tile
        :return: Nothing
        """
        grab = None

        rx = range(self._tiles_rectangle.width())
        ry = range(self._tiles_rectangle.height())

        for x, y in product(rx, ry):
            tp = Point(self._tiles_rectangle.topLeft() + QPoint(x, y))
            if tp not in self._tile_pixmaps:
                grab = QPoint(tp)
                break

        if grab is None:
            self._url = QUrl()
            return

        path = 'http://tile.openstreetmap.org/%d/%d/%d.png' % (self.zoom, grab.x(), grab.y())
        self._url = QUrl(path)
        self.request = QNetworkRequest()
        self.request.setUrl(self._url)
        self.request.setRawHeader(b'User-Agent', b'Nokia (PyQt) Graphics Dojo 1.0')
        self.request.setAttribute(QNetworkRequest.User, grab)
        self._manager.get(self.request)

        print('downloading z:', self.zoom, 'x:', grab.x(), 'y:', grab.y())

    def tile_rectangle(self, tp: Point):
        """
        Get tile rectangle
        :param tp: Tile point
        :return: QRect instance
        """
        t = tp - self._tiles_rectangle.topLeft()
        x = t.x() * TDIM + self._offset.x()
        y = t.y() * TDIM + self._offset.y()

        return QRect(x, y, TDIM, TDIM)


class LightMaps(QWidget):

    def __init__(self, parent=None):
        """

        :param parent:
        """
        super(LightMaps, self).__init__(parent)

        self.pressed = False
        self.snapped = False
        self.zoomed = False
        self.invert = False

        self._normalMap = SlippyMap(self)

        self.pressPos = QPoint()

        self.dragPos = QPoint()

        self.tapTimer = QBasicTimer()

        self.zoomPixmap = QPixmap()

        self.maskPixmap = QPixmap()

        self._normalMap.updated.connect(self.update_map)

    def set_center(self, lat, lng):
        self._normalMap.latitude = lat
        self._normalMap.longitude = lng
        self._normalMap.invalidate()

    # slots
    def toggle_night_mode(self):
        self.invert = not self.invert
        self.update()

    def update_map(self, r):
        self.update(r)

    def resizeEvent(self, event):
        self._normalMap.width = self.width()
        self._normalMap.height = self.height()
        self._normalMap.invalidate()

    def set_zoom(self, zoom_level):

        if 2 < zoom_level <= 15:
            self._normalMap.zoom = zoom_level
            self.update()

            print('Zoom at:', self._normalMap.zoom)

    def zoom_increase(self):
        inc = 1
        if self._normalMap.zoom + inc <= 15:
            self._normalMap.zoom += inc
            self._normalMap.invalidate()
            self.update()

            print('Zoom at:', self._normalMap.zoom)

    def zoom_decrease(self):
        inc = 1
        if self._normalMap.zoom - inc > 2:
            self._normalMap.zoom -= inc
            self._normalMap.invalidate()
            # self._normalMap.
            self.update()

            print('Zoom at:', self._normalMap.zoom)

    def paintEvent(self, event):
        p = QPainter()
        p.begin(self)
        self._normalMap.render(p, event.rect())

        p.setPen(Qt.black)
        p.drawText(self.rect(), Qt.AlignBottom | Qt.TextWordWrap, "GridCal, Map data CCBYSA 2009 "
                                                                  "OpenStreetMap.org contributors")
        p.end()

        if self.invert:
            p = QPainter(self)
            p.setCompositionMode(QPainter.CompositionMode_Difference)
            p.fillRect(event.rect(), Qt.white)
            p.end()

    def mousePressEvent(self, event):
        """

        :param event:
        :return:
        """
        if event.buttons() != Qt.LeftButton:
            return

        self.pressed = self.snapped = True
        self.pressPos = self.dragPos = event.pos()
        # self.tapTimer.stop()
        # self.tapTimer.start(HOLD_TIME, self)

        tx = event.pos().x()
        ty = event.pos().y()
        lat = latitude_from_tile(ty, self._normalMap.zoom)
        lon = longitude_from_tile(tx, self._normalMap.zoom)
        print(tx, ty, lat, lon)

    def mouseMoveEvent(self, event):
        """

        :param event:
        :return:
        """
        if not event.buttons():
            return

        if not self.zoomed:
            if not self.pressed or not self.snapped:
                delta = event.pos() - self.pressPos
                self.pressPos = event.pos()
                self._normalMap.pan(delta)
                return
            else:
                threshold = 10
                delta = event.pos() - self.pressPos
                self.snapped = False
                if self.snapped:
                    self.snapped &= delta.x() < threshold
                    self.snapped &= delta.y() < threshold
                    self.snapped &= delta.x() > -threshold
                    self.snapped &= delta.y() > -threshold

        else:
            self.dragPos = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        """

        :param event:
        :return:
        """
        self.zoomed = False
        self.update()

    def keyPressEvent(self, event):
        """

        :param event:
        :return:
        """
        if not self.zoomed:
            if event.key() == Qt.Key_Left:
                self._normalMap.pan(QPoint(20, 0))
            if event.key() == Qt.Key_Right:
                self._normalMap.pan(QPoint(-20, 0))
            if event.key() == Qt.Key_Up:
                self._normalMap.pan(QPoint(0, 20))
            if event.key() == Qt.Key_Down:
                self._normalMap.pan(QPoint(0, -20))
            if event.key() == Qt.Key_Z or event.key() == Qt.Key_Select:
                self.dragPos = QPoint(self.width() / 2, self.height() / 2)
                # self.activate_magnifying_glass()
        else:
            if event.key() == Qt.Key_Z or event.key() == Qt.Key_Select:
                self.zoomed = False
                self.update()

            delta = QPoint(0, 0)
            if event.key() == Qt.Key_Left:
                delta = QPoint(-15, 0)
            if event.key() == Qt.Key_Right:
                delta = QPoint(15, 0)
            if event.key() == Qt.Key_Up:
                delta = QPoint(0, -15)
            if event.key() == Qt.Key_Down:
                delta = QPoint(0, 15)
            if delta != QPoint(0, 0):
                self.dragPos += delta
                self.update()
