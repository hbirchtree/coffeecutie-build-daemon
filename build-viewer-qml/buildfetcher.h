#include <QObject>
#include <QStringListModel>
#include <QtNetwork/QNetworkAccessManager>
#include <QtNetwork/QNetworkRequest>

class BuildInformationFetcher : public QStringListModel
{
    Q_OBJECT
    Q_PROPERTY(QString server READ server WRITE setServer NOTIFY serverChanged)
    Q_PROPERTY(bool fetching READ fetching NOTIFY fetchingChanged)

    bool m_fetching;
    QString m_server;

public:
    BuildInformationFetcher(QObject* parent = nullptr):
        QStringListModel(parent),
        m_fetching(true)
    {
    }

    ~BuildInformationFetcher()
    {
    }

    bool fetching() const
    {
        return m_fetching;
    }

    QString server() const
    {
        return m_server;
    }

public slots:
    void setServer(QString server)
    {
        if (m_server == server)
            return;

        m_server = server;
        emit serverChanged(server);
    }

signals:
    void fetchingChanged(bool fetching);
    void serverChanged(QString server);
};
