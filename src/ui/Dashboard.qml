import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ApplicationWindow {
    id: root
    width: 1180
    height: 740
    minimumWidth: 960
    minimumHeight: 620
    visible: true
    title: "Ultimate Commander OS"
    color: "#0C0C0D"

    font.family: "Segoe UI Variable Display"

    background: Rectangle {
        gradient: Gradient {
            GradientStop { position: 0.0; color: "#141416" }
            GradientStop { position: 1.0; color: "#0C0C0D" }
        }
    }

    function metricColor(v) {
        if (v >= 90) return "#FF99A4"
        if (v >= 70) return "#FCE100"
        return "#60CDFF"
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            color: "transparent"

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 24
                spacing: 18

                RowLayout {
                    Layout.fillWidth: true
                    spacing: 16

                    ColumnLayout {
                        spacing: 4
                        Label {
                            text: "Ultimate Commander OS"
                            color: "#F3F3F3"
                            font.pixelSize: 28
                            font.weight: Font.DemiBold
                        }
                        Label {
                            text: (typeof backend !== "undefined" ? backend.system : "Windows")
                                  + "  ·  " + (typeof backend !== "undefined" ? backend.hostname : "")
                            color: "#C5C5C5"
                            font.pixelSize: 13
                        }
                    }
                    Item { Layout.fillWidth: true }
                    Button {
                        text: "UI neu laden"
                        onClicked: if (typeof backend !== "undefined") backend.reloadUi()
                        background: Rectangle {
                            radius: 8
                            color: parent.down ? "#4CC2FF" : "#60CDFF"
                        }
                        contentItem: Text {
                            text: parent.text
                            color: "#0C0C0D"
                            font.family: "Segoe UI Variable"
                            font.pixelSize: 13
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                        }
                    }
                }

                GridLayout {
                    Layout.fillWidth: true
                    columns: 3
                    columnSpacing: 16
                    rowSpacing: 16

                    Repeater {
                        model: [
                            { title: "CPU", value: typeof backend !== "undefined" ? backend.cpu : 0, unit: "%" },
                            { title: "RAM", value: typeof backend !== "undefined" ? backend.ram : 0, unit: "%" },
                            { title: "Datenträger", value: typeof backend !== "undefined" ? backend.disk : 0, unit: "%" }
                        ]
                        delegate: Rectangle {
                            Layout.fillWidth: true
                            implicitHeight: 148
                            radius: 12
                            color: "#CC222226"
                            border.color: "#33FFFFFF"
                            border.width: 1

                            ColumnLayout {
                                anchors.fill: parent
                                anchors.margins: 18
                                spacing: 10
                                Label {
                                    text: modelData.title
                                    color: "#C5C5C5"
                                    font.pixelSize: 13
                                }
                                Label {
                                    text: Math.round(modelData.value) + modelData.unit
                                    color: "#F3F3F3"
                                    font.pixelSize: 36
                                    font.weight: Font.DemiBold
                                }
                                Rectangle {
                                    Layout.fillWidth: true
                                    height: 6
                                    radius: 3
                                    color: "#33FFFFFF"
                                    Rectangle {
                                        width: parent.width * Math.min(Math.max(modelData.value / 100, 0), 1)
                                        height: parent.height
                                        radius: 3
                                        color: root.metricColor(modelData.value)
                                    }
                                }
                            }
                        }
                    }
                }

                RowLayout {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    spacing: 16

                    Rectangle {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        radius: 12
                        color: "#CC222226"
                        border.color: "#33FFFFFF"
                        border.width: 1

                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: 20
                            spacing: 12
                            Label {
                                text: "Netzwerk"
                                color: "#F3F3F3"
                                font.pixelSize: 18
                                font.weight: Font.DemiBold
                            }
                            Label {
                                text: typeof backend !== "undefined" ? backend.net : "offline"
                                color: "#60CDFF"
                                font.pixelSize: 15
                            }
                            Label {
                                text: (typeof backend !== "undefined" ? backend.cores : 0) + " logische Kerne  ·  Live-Polling 1s"
                                color: "#C5C5C5"
                                font.pixelSize: 13
                            }
                            Label {
                                Layout.fillWidth: true
                                wrapMode: Text.WordWrap
                                text: "Adapterliste kommt aus ifaddr (kein netifaces / kein C-Compiler). Fallback: psutil."
                                color: "#C5C5C5"
                                font.pixelSize: 12
                            }
                            Item { Layout.fillHeight: true }
                        }
                    }

                    Rectangle {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        radius: 12
                        color: "#CC222226"
                        border.color: "#33FFFFFF"
                        border.width: 1

                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: 20
                            spacing: 12
                            Label {
                                text: "KI-Schicht"
                                color: "#F3F3F3"
                                font.pixelSize: 18
                                font.weight: Font.DemiBold
                            }
                            Label {
                                text: typeof backend !== "undefined" ? backend.ollama : "…"
                                color: "#6CCB5F"
                                font.pixelSize: 15
                                wrapMode: Text.WordWrap
                                Layout.fillWidth: true
                            }
                            Label {
                                Layout.fillWidth: true
                                wrapMode: Text.WordWrap
                                text: "Ollama optional. Fehlt der Dienst, bleibt der Mock-Modus aktiv — die Oberfläche läuft weiter."
                                color: "#C5C5C5"
                                font.pixelSize: 12
                            }
                            TextField {
                                id: prompt
                                Layout.fillWidth: true
                                placeholderText: "Befehl an die lokale KI…"
                                color: "#F3F3F3"
                                placeholderTextColor: "#888"
                                background: Rectangle {
                                    radius: 8
                                    color: "#1A1A1C"
                                    border.color: "#33FFFFFF"
                                }
                                onAccepted: {
                                    if (typeof backend !== "undefined")
                                        reply.text = backend.ask(prompt.text)
                                }
                            }
                            Label {
                                id: reply
                                Layout.fillWidth: true
                                wrapMode: Text.WordWrap
                                color: "#F3F3F3"
                                font.pixelSize: 12
                                text: ""
                            }
                            Item { Layout.fillHeight: true }
                        }
                    }
                }
            }
        }

        StatusBar {
            Layout.fillWidth: true
            hostname: typeof backend !== "undefined" ? backend.hostname : "host"
            net: typeof backend !== "undefined" ? backend.net : "offline"
            ollama: typeof backend !== "undefined" ? backend.ollama : "…"
            status: typeof backend !== "undefined" ? backend.status : "boot"
            cpu: typeof backend !== "undefined" ? backend.cpu : 0
            ram: typeof backend !== "undefined" ? backend.ram : 0
        }
    }

    Connections {
        target: typeof backend !== "undefined" ? backend : null
        function onReloadRequested(token) {
            root.title = "Ultimate Commander OS · reload #" + token
        }
    }
}
