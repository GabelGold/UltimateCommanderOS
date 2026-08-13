import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: bar
    property string hostname: "host"
    property string net: "offline"
    property string ollama: "…"
    property string status: "boot"
    property real cpu: 0
    property real ram: 0

    height: 36
    color: "#E01C1C1E"
    radius: 0

    RowLayout {
        anchors.fill: parent
        anchors.leftMargin: 16
        anchors.rightMargin: 16
        spacing: 16

        Label {
            text: bar.hostname
            color: "#F3F3F3"
            font.family: "Segoe UI Variable"
            font.pixelSize: 12
        }
        Rectangle { width: 1; height: 14; color: "#33FFFFFF" }
        Label {
            text: "CPU " + Math.round(bar.cpu) + "%"
            color: "#C5C5C5"
            font.family: "Segoe UI Variable"
            font.pixelSize: 12
        }
        Label {
            text: "RAM " + Math.round(bar.ram) + "%"
            color: "#C5C5C5"
            font.family: "Segoe UI Variable"
            font.pixelSize: 12
        }
        Item { Layout.fillWidth: true }
        Label {
            text: bar.net
            color: "#60CDFF"
            font.family: "Segoe UI Variable"
            font.pixelSize: 12
        }
        Rectangle { width: 1; height: 14; color: "#33FFFFFF" }
        Label {
            text: bar.ollama
            color: "#6CCB5F"
            font.family: "Segoe UI Variable"
            font.pixelSize: 12
        }
        Rectangle {
            width: 8; height: 8; radius: 4
            color: bar.status === "ready" ? "#6CCB5F" : "#FCE100"
        }
    }
}
