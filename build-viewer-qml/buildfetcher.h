#include <QObject>
#include <QJsonDocument>
#include <QJsonObject>
#include <QJsonArray>
#include <QStandardItemModel>
#include <QtNetwork/QNetworkAccessManager>
#include <QtNetwork/QNetworkRequest>
#include <QtNetwork/QNetworkReply>

class BuildInformationFetcher : public QStandardItemModel
{
    Q_OBJECT
    Q_PROPERTY(QString server READ server WRITE setServer NOTIFY serverChanged)
    Q_PROPERTY(int serverPort READ serverPort WRITE setServerPort NOTIFY serverPortChanged)
    Q_PROPERTY(bool fetching READ fetching NOTIFY fetchingChanged)

    bool m_fetching;
    QString m_server;

    int m_serverPort;

    QNetworkAccessManager m_nman;

public:
    enum BuildRoles
    {
	BuildId = Qt::UserRole + 1,
	CommitId,
	HasBinary,
	HostId,
	PlatformId,
	StatusId,
	TimeId,
	ColorId,
    };

    BuildInformationFetcher(QObject* parent = nullptr):
	QStandardItemModel(parent),
        m_fetching(true)
    {
	setColumnCount(7);

	QHash<int,QByteArray> roles;
	roles[BuildId] = "bid";
	roles[CommitId] = "commit";
	roles[HasBinary] = "has_bin";
	roles[HostId] = "host";
	roles[PlatformId] = "platform";
	roles[StatusId] = "status";
	roles[TimeId] = "timest";
	roles[ColorId] = "colorCode";
	setItemRoleNames(roles);
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

    int serverPort() const
    {
	return m_serverPort;
    }

public slots:
    void update()
    {
	QUrl url(QString("http://%1:%2/rest/all")
		 .arg(m_server)
		 .arg(m_serverPort));

	QNetworkRequest req;
	req.setUrl(url);

	QNetworkReply* rep = m_nman.get(req);
	connect(rep,&QNetworkReply::finished,this,&BuildInformationFetcher::receiveUpdate);

	m_fetching = true;
	fetchingChanged(m_fetching);
    }

    void receiveUpdate()
    {
	QNetworkReply* rep = static_cast<QNetworkReply*>(sender());

	if(rep)
	{
	    this->removeRows(0,rowCount());

	    QByteArray data = rep->readAll();

	    QJsonParseError err;
	    QJsonDocument doc = QJsonDocument::fromJson(data,&err);

	    if(err.error == QJsonParseError::NoError)
	    {
		QJsonArray const& elements = doc.object()["logs"].toArray();
		for(QJsonValue const& obj : elements)
		{
		    QStandardItem* it = new QStandardItem;
		    QJsonObject b = obj.toObject();

		    it->setData(b["bid"].toVariant().toULongLong(),BuildId);
		    it->setData(b["commit"].toString().mid(0,10),CommitId);
		    it->setData(b["has_binary"].toBool(),HasBinary);
		    it->setData(b["host"].toString(),HostId);
		    it->setData(b["platform"].toString(),PlatformId);
		    it->setData(b["status"].toInt(),StatusId);
		    it->setData(QDateTime::fromMSecsSinceEpoch(
				    b["time"].toVariant().toULongLong()*1000),
				TimeId);

		    if(b["status"].toInt() == 0)
			it->setData(QColor("green"),ColorId);
		    else
			it->setData(QColor("red"),ColorId);

		    appendRow(it);
		}
	    }else
		qDebug("Parsing error: %s",err.errorString().toStdString().c_str());

	    rep->deleteLater();
	    m_fetching = false;
	    fetchingChanged(m_fetching);
	}else{
	    qDebug("Please no.");
	}
    }

    void setServer(QString server)
    {
        if (m_server == server)
            return;

        m_server = server;
        emit serverChanged(server);
    }

    void setServerPort(int serverPort)
    {
	if (m_serverPort == serverPort)
	    return;

	m_serverPort = serverPort;
	emit serverPortChanged(serverPort);
    }

signals:
    void fetchingChanged(bool fetching);
    void serverChanged(QString server);
    void serverPortChanged(int serverPort);
};
