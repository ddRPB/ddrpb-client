#### ##     ## ########   #######  ########  ########  ######
 ##  ###   ### ##     ## ##     ## ##     ##    ##    ##    ##
 ##  #### #### ##     ## ##     ## ##     ##    ##    ##
 ##  ## ### ## ########  ##     ## ########     ##     ######
 ##  ##     ## ##        ##     ## ##   ##      ##          ##
 ##  ##     ## ##        ##     ## ##    ##     ##    ##    ##
#### ##     ## ##         #######  ##     ##    ##     ######

# ORM
from sqlalchemy import Column, Sequence, Integer, String, Boolean, DateTime, ForeignKey, Unicode
from sqlalchemy import create_engine
from sqlalchemy import text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, scoped_session
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound

# Utils
from utils.JsonSerializer import JsonSerializer

######## ##    ## ######## #### ######## #### ########  ######
##       ###   ##    ##     ##     ##     ##  ##       ##    ##
##       ####  ##    ##     ##     ##     ##  ##       ##
######   ## ## ##    ##     ##     ##     ##  ######    ######
##       ##  ####    ##     ##     ##     ##  ##             ##
##       ##   ###    ##     ##     ##     ##  ##       ##    ##
######## ##    ##    ##    ####    ##    #### ########  ######

Base = declarative_base()

 ######  ######## ########  ##     ##  ######  ######## ######## ##    ## ########  ######## 
##    ##    ##    ##     ## ##     ## ##    ##    ##       ##     ##  ##  ##     ## ##       
##          ##    ##     ## ##     ## ##          ##       ##      ####   ##     ## ##       
 ######     ##    ########  ##     ## ##          ##       ##       ##    ########  ######   
      ##    ##    ##   ##   ##     ## ##          ##       ##       ##    ##        ##       
##    ##    ##    ##    ##  ##     ## ##    ##    ##       ##       ##    ##        ##       
 ######     ##    ##     ##  #######   ######     ##       ##       ##    ##        ######## 


class RTStructType(Base):
    """DICOM RT structure type
    """
    __tablename__ = "rtstructtype"

    id = Column(Integer, Sequence("rtstructtype_id_seq"), primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(String(255))


class RTStructTypeSerializer(JsonSerializer):
    __attributes__ = ["id", "name", "description"]
    __required__ = []
    __attribute_serializer__ = dict()
    __object_class__ = RTStructType

########  ########  ######  ######## ########  ##     ##  ######  ######## 
##     ##    ##    ##    ##    ##    ##     ## ##     ## ##    ##    ##    
##     ##    ##    ##          ##    ##     ## ##     ## ##          ##    
########     ##     ######     ##    ########  ##     ## ##          ##    
##   ##      ##          ##    ##    ##   ##   ##     ## ##          ##    
##    ##     ##    ##    ##    ##    ##    ##  ##     ## ##    ##    ##    
##     ##    ##     ######     ##    ##     ##  #######   ######     ##    


class RTStruct(Base):
    """DICOM RT structure
    """
    __tablename__ = "rtstruct"

    id = Column(Integer, Sequence("rtstruct_id_seq"), primary_key=True)
    identifier = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(String(255))

    typeid = Column(Integer, ForeignKey('rtstructtype.id'))

    structType = relationship(RTStructType, primaryjoin=typeid == RTStructType.id)


class RTStructSerializer(JsonSerializer):
    __attributes__ = ["id", "identifier", "name", "description", "structType"]
    __required__ = ["identifier", "name"]
    __attribute_serializer__ = dict(structType = "structType")
    __object_class__ = RTStruct

    def __init__(self, timezone=None):
        super(RTStructSerializer, self).__init__(timezone)
        self.serializers["structType"] = dict(
            serialize=lambda x:
                RTStructTypeSerializer(timezone).serialize(x),
            deserialize=lambda x:
                RTStructTypeSerializer(timezone).deserialize(x)
        )
   ###    ##    ##  #######  ######## ##    ## ########  ######## 
  ## ##   ###   ## ##     ##    ##     ##  ##  ##     ## ##       
 ##   ##  ####  ## ##     ##    ##      ####   ##     ## ##       
##     ## ## ## ## ##     ##    ##       ##    ########  ######   
######### ##  #### ##     ##    ##       ##    ##        ##       
##     ## ##   ### ##     ##    ##       ##    ##        ##       
##     ## ##    ##  #######     ##       ##    ##        ######## 


class AnnotationType(Base):
    """Annotation Type for eCRF fields
    """
    __tablename__ = "annotationtype"

    id = Column(Integer, Sequence("annotationtype_id_seq"), primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(String(255))


class AnnotationTypeSerializer(JsonSerializer):
    __attributes__ = ["id", "name", "description"]
    __required__ = []
    __attribute_serializer__ = dict()
    __object_class__ = AnnotationType

 ######  ######## ########  ##     ## ######## ########
##    ## ##       ##     ## ##     ## ##       ##     ##
##       ##       ##     ## ##     ## ##       ##     ##
 ######  ######   ########  ##     ## ######   ########
      ## ##       ##   ##    ##   ##  ##       ##   ##
##    ## ##       ##    ##    ## ##   ##       ##    ##
 ######  ######## ##     ##    ###    ######## ##     ##


class ServerIE(Base):
    """Partner Site RadPlanBio server for import/export
    """
    __tablename__ = "serverie"

    serverid = Column(Integer, Sequence("serverie_serverid_seq"), primary_key=True)
    ipaddress = Column(String(255), nullable=False)
    port = Column(Integer, nullable=False)
    isenabled = Column(Boolean)


class ServerIESerializer(JsonSerializer):
    __attributes__ = ["serverid", "ipaddress", "port"]
    __required__ = []
    __attribute_serializer__ = dict()
    __object_class__ = ServerIE

########     ###     ######   ######  
##     ##   ## ##   ##    ## ##    ## 
##     ##  ##   ##  ##       ##       
########  ##     ## ##        ######  
##        ######### ##             ## 
##        ##     ## ##    ## ##    ## 
##        ##     ##  ######   ######  


class Pacs(Base):
    """PACS - Conquest
    """
    __tablename__ = "pacs"

    pacsid = Column(Integer, Sequence("pacs_pacsid_seq"), primary_key=True)
    pacsbaseurl = Column(String(255), nullable=False)
    isenabled = Column(Boolean)


class PacsSerializer(JsonSerializer):
    __attributes__ = ["pacsid", "pacsbaseurl"]
    __required__ = []
    __attribute_serializer__ = dict()
    __object_class__ = Pacs

########   #######  ########  ########    ###    ##       
##     ## ##     ## ##     ##    ##      ## ##   ##       
##     ## ##     ## ##     ##    ##     ##   ##  ##       
########  ##     ## ########     ##    ##     ## ##       
##        ##     ## ##   ##      ##    ######### ##       
##        ##     ## ##    ##     ##    ##     ## ##       
##         #######  ##     ##    ##    ##     ## ######## 


class Portal(Base):
    """RPB Portal
    """
    __tablename__ = "portal"

    portalid = Column(Integer, Sequence("portal_portalid_seq"), primary_key=True)
    portalbaseurl = Column(String(255), nullable=False)
    publicurl = Column(String(255))
    isenabled = Column(Boolean)

    # I do not support such relationships in serialisation
    #software = relationship("Software")


class PortalSerializer(JsonSerializer):
    __attributes__ = ["portalid", "portalbaseurl", "publicurl"]
    __required__ = []
    __attribute_serializer__ = dict()
    __object_class__ = Portal

 ######   #######  ######## ######## ##      ##    ###    ########  ######## 
##    ## ##     ## ##          ##    ##  ##  ##   ## ##   ##     ## ##       
##       ##     ## ##          ##    ##  ##  ##  ##   ##  ##     ## ##       
 ######  ##     ## ######      ##    ##  ##  ## ##     ## ########  ######   
      ## ##     ## ##          ##    ##  ##  ## ######### ##   ##   ##       
##    ## ##     ## ##          ##    ##  ##  ## ##     ## ##    ##  ##       
 ######   #######  ##          ##     ###  ###  ##     ## ##     ## ########


class Software(Base):
    """Software
    """
    __tablename__ = "software"

    id = Column(Integer, Sequence("software_id_seq"), primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(String(255))
    version = Column(String(255))
    filename = Column(String(255))
    latest = Column(Boolean)

    portalid = Column(Integer, ForeignKey('portal.portalid'))

    portal = relationship(Portal, primaryjoin=portalid == Portal.portalid)


class SoftwareSerializer(JsonSerializer):
    __attributes__ = ["id", "name", "description", "version", "filename", "latest", "portal"]
    __required__ = ["name"]
    __attribute_serializer__ = dict(portal = "portal")
    __object_class__ = Software

    def __init__(self, timezone=None):
        super(SoftwareSerializer, self).__init__(timezone)
        self.serializers["portal"] = dict(
            serialize=lambda x:
                PortalSerializer(timezone).serialize(x),
            deserialize=lambda x:
                PortalSerializer(timezone).deserialize(x)
        )

######## ########   ######  
##       ##     ## ##    ## 
##       ##     ## ##       
######   ##     ## ##       
##       ##     ## ##       
##       ##     ## ##    ## 
######## ########   ######  


class Edc(Base):
    """Electronic Data Capture (EDC) domain object
    EDC stores connection setting to OpenClinica system
    """
    __tablename__ = "edc"

    edcid = Column(Integer, Sequence("edc_edcid_seq"), primary_key=True)
    edcbaseurl = Column(String(255), nullable=False)
    edcpublicurl = Column(String(255))
    soapbaseurl = Column(String(255), nullable=False)
    soappublicurl = Column(String(255))
    isenabled = Column(Boolean)
    version = Column(String(15))


class EdcSerializer(JsonSerializer):
    """Electronic Data Capture (EDC) domain object serializer
    """
    __attributes__ = ["edcid", "edcbaseurl", "edcpublicurl", "soapbaseurl", "soappublicurl", "isenabled", "version"]
    __required__ = []
    __attribute_serializer__ = dict()
    __object_class__ = Edc

########  #### ########   ######   
##     ##  ##  ##     ## ##    ##  
##     ##  ##  ##     ## ##        
########   ##  ##     ## ##   #### 
##         ##  ##     ## ##    ##  
##         ##  ##     ## ##    ##  
##        #### ########   ######   


class Pidg(Base):
    """PIDG - mainzelliste
    """
    __tablename__ = "pidg"

    generatorid = Column(Integer, Sequence("pidg_generatorid_seq"), primary_key=True)
    generatorbaseurl = Column(String(255), nullable=False)
    apikey = Column(String(255), nullable=False)
    adminusername = Column(String(255), nullable=False)
    adminpassword = Column(String(255), nullable=False)
    isenabled = Column(Boolean)


class PidgSerializer(JsonSerializer):
    __attributes__ = ["generatorid", "generatorbaseurl", "apikey", "adminusername", "adminpassword"]
    __required__ = []
    __attribute_serializer__ = dict()
    __object_class__ = Pidg

########     ###    ########  ######## ##    ## ######## ########      ######  #### ######## ########
##     ##   ## ##   ##     ##    ##    ###   ## ##       ##     ##    ##    ##  ##     ##    ##
##     ##  ##   ##  ##     ##    ##    ####  ## ##       ##     ##    ##        ##     ##    ##
########  ##     ## ########     ##    ## ## ## ######   ########      ######   ##     ##    ######
##        ######### ##   ##      ##    ##  #### ##       ##   ##            ##  ##     ##    ##
##        ##     ## ##    ##     ##    ##   ### ##       ##    ##     ##    ##  ##     ##    ##
##        ##     ## ##     ##    ##    ##    ## ######## ##     ##     ######  ####    ##    ########


class PartnerSite(Base):
    """PartnerSite
    """
    __tablename__ = "partnersite"

    siteid = Column(Integer, Sequence("partnersite_siteid_seq"), primary_key=True)
    identifier = Column(String(10), nullable=False)
    sitename = Column(String(255), nullable=False)
    description = Column(String(255))
    isenabled = Column(Boolean)

    serverid = Column(Integer, ForeignKey('serverie.serverid'))
    pacsid = Column(Integer, ForeignKey('pacs.pacsid'))
    portalid = Column(Integer, ForeignKey('portal.portalid'))
    generatorid = Column(Integer, ForeignKey('pidg.generatorid'))
    edcid = Column(Integer, ForeignKey('edc.edcid'))

    serverie = relationship(ServerIE, primaryjoin=serverid == ServerIE.serverid)
    pacs = relationship(Pacs, primaryjoin=pacsid == Pacs.pacsid)
    portal = relationship(Portal, primaryjoin=portalid == Portal.portalid)
    pidg = relationship(Pidg, primaryjoin=generatorid == Pidg.generatorid)
    edc = relationship(Edc, primaryjoin=edcid == Edc.edcid)


class PartnerSiteSerializer(JsonSerializer):
    __attributes__ = ["siteid", "identifier", "sitename", "serverie", "pacs", "portal", "pidg", "edc"]
    __required__ = ["sitename"]
    __attribute_serializer__ = dict(serverie = "serverie", pacs = "pacs", portal="portal", pidg = "pidg", edc = "edc")
    __object_class__ = PartnerSite

    def __init__(self, timezone=None):
        super(PartnerSiteSerializer, self).__init__(timezone)
        self.serializers['serverie'] = dict(
            serialize=lambda x:
                ServerIESerializer(timezone).serialize(x),
            deserialize=lambda x:
                ServerIESerializer(timezone).deserialize(x)
        )
        self.serializers['pacs'] = dict(
            serialize=lambda x:
                PacsSerializer(timezone).serialize(x),
            deserialize=lambda x:
                PacsSerializer(timezone).deserialize(x)
        )
        self.serializers['portal'] = dict(
            serialize=lambda x:
                PortalSerializer(timezone).serialize(x),
            deserialize=lambda x:
                PortalSerializer(timezone).deserialize(x)
        )
        self.serializers['pidg'] = dict(
            serialize=lambda x:
                PidgSerializer(timezone).serialize(x),
            deserialize=lambda x:
                PidgSerializer(timezone).deserialize(x)
        )
        self.serializers['edc'] = dict(
            serialize=lambda x:
                EdcSerializer(timezone).serialize(x),
            deserialize=lambda x:
                EdcSerializer(timezone).deserialize(x)
        )

   ###     ######   ######   #######  ##     ## ##    ## ########
  ## ##   ##    ## ##    ## ##     ## ##     ## ###   ##    ##
 ##   ##  ##       ##       ##     ## ##     ## ####  ##    ##
##     ## ##       ##       ##     ## ##     ## ## ## ##    ##
######### ##       ##       ##     ## ##     ## ##  ####    ##
##     ## ##    ## ##    ## ##     ## ##     ## ##   ###    ##
##     ##  ######   ######   #######   #######  ##    ##    ##


class DefaultAccount(Base):
    """Default user account in RadPlanBio platform
    not connected to OpenClinica or anything else
    """
    __tablename__ = 'defaultaccount'

    id = Column(Integer, Sequence('account_id_seq'), primary_key=True)
    username = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)
    isenabled = Column(Boolean)
    ocusername = Column(String(255))
    ocpasswordhash = ""
    apikey= ""

    partnersiteid = Column(Integer, ForeignKey('partnersite.siteid'))

    partnersite = relationship(PartnerSite, primaryjoin=partnersiteid == PartnerSite.siteid)

    def __repr__(self):
        pass
        #return "<User('%s','%s', '%b')>" % (self.username, self.password, self.isenabled)


class DefaultAccountSerializer(JsonSerializer):
    __attributes__ = ["id", "username", "isenabled", "ocusername", "ocpasswordhash", "apikey", "partnersite"]
    __required__ = [""]
    __attribute_serializer__ = dict(partnersite = "partnersite")
    __object_class__ = DefaultAccount

    def __init__(self, timezone=None):
        super(DefaultAccountSerializer, self).__init__(timezone)
        self.serializers['partnersite'] = dict(
            serialize=lambda x:
                PartnerSiteSerializer(timezone).serialize(x),
            deserialize=lambda x:
                PartnerSiteSerializer(timezone).deserialize(x)
        )

 ######  ######## ##     ## ########  ##    ##
##    ##    ##    ##     ## ##     ##  ##  ##
##          ##    ##     ## ##     ##   ####
 ######     ##    ##     ## ##     ##    ##
      ##    ##    ##     ## ##     ##    ##
##    ##    ##    ##     ## ##     ##    ##
 ######     ##     #######  ########     ##


class Study(Base):
    """RadPlanBio study
    """
    __tablename__ = "study"

    id = Column(Integer, Sequence("study_id_seq"), primary_key=True)
    ocstudyidentifier = Column(Unicode, nullable=False)

    siteid = Column(Integer, ForeignKey('partnersite.siteid'))

    partnersite = relationship(PartnerSite, primaryjoin=siteid == PartnerSite.siteid)


class StudySerializer(JsonSerializer):
    __attributes__ = ["id", "ocstudyidentifier", "partnersite"]
    __required__ = [""]
    __attribute_serializer__ = dict(partnersite = "partnersite")
    __object_class__ = Study

    def __init__(self, timezone=None):
        super(StudySerializer, self).__init__(timezone)
        self.serializers["partnersite"] = dict(
            serialize=lambda x:
                PartnerSiteSerializer(timezone).serialize(x),
            deserialize=lambda x:
                PartnerSiteSerializer(timezone).deserialize(x)
        )


class OCStudy(Base):
    """OpenClinica study
    """
    __tablename__ = "not_used"

    id = Column(Integer, Sequence("study_id_seq"), primary_key=True)
    uniqueIdentifier = ""
    secondaryIdentifier = ""
    name = ""
    ocoid = ""
    parentStudy = None


class OCStudySerializer(JsonSerializer):
    __attributes__ = ["id", "uniqueIdentifier", "secondaryIdentifier", "name", "ocoid"]
    __required__ = [""]
    __attribute_serializer__ = dict()
    __object_class__ = OCStudy

    def __init__(self, timezone=None):
        super(OCStudySerializer, self).__init__(timezone)

   ###    ##    ## ##    ##  #######  ########    ###    ######## ####  #######  ##    ## 
  ## ##   ###   ## ###   ## ##     ##    ##      ## ##      ##     ##  ##     ## ###   ## 
 ##   ##  ####  ## ####  ## ##     ##    ##     ##   ##     ##     ##  ##     ## ####  ## 
##     ## ## ## ## ## ## ## ##     ##    ##    ##     ##    ##     ##  ##     ## ## ## ## 
######### ##  #### ##  #### ##     ##    ##    #########    ##     ##  ##     ## ##  #### 
##     ## ##   ### ##   ### ##     ##    ##    ##     ##    ##     ##  ##     ## ##   ### 
##     ## ##    ## ##    ##  #######     ##    ##     ##    ##    ####  #######  ##    ## 


class CrfFieldAnnotation(Base):
    """CrfFieldAnnotation for OpenClinica eCRF fields (like DICOM StudyInstance UID, etc.)
    """

    __tablename__ = "crffieldannotation"

    id = Column(Integer, Sequence("crffieldannotation_id_seq"), primary_key=True)
    eventdefinitionoid = Column(String(255))
    formoid = Column(String(255))
    groupoid = Column(String(255))
    crfitemoid = Column(String(255))

    typeid = Column(Integer, ForeignKey("annotationtype.id"))
    studyid = Column(Integer, ForeignKey("study.id"))

    annotationtype = relationship(AnnotationType, primaryjoin=typeid == AnnotationType.id)
    study = relationship(Study, primaryjoin=studyid == Study.id)


class CrfFieldAnnotationSerializer(JsonSerializer):
    __attributes__ = ["id", "eventdefinitionoid", "formoid", "groupoid", "crfitemoid", "annotationtype", "study"]
    __required__ = [""]
    __attribute_serializer__ = dict(annotationtype = "annotationtype", study = "study")
    __object_class__ = CrfFieldAnnotation

    def __init__(self, timezone=None):
        super(CrfFieldAnnotationSerializer, self).__init__(timezone)
        self.serializers["annotationtype"] = dict(
            serialize=lambda x:
                AnnotationTypeSerializer(timezone).serialize(x),
            deserialize=lambda x:
                AnnotationTypeSerializer(timezone).deserialize(x)
        )
        self.serializers["study"] = dict(
            serialize=lambda x:
                StudySerializer(timezone).serialize(x),
            deserialize=lambda x:
                StudySerializer(timezone).deserialize(x)
        )

 ######  ######## ########  ##     ## ####  ######  ########
##    ## ##       ##     ## ##     ##  ##  ##    ## ##
##       ##       ##     ## ##     ##  ##  ##       ##
 ######  ######   ########  ##     ##  ##  ##       ######
      ## ##       ##   ##    ##   ##   ##  ##       ##
##    ## ##       ##    ##    ## ##    ##  ##    ## ##
 ######  ######## ##     ##    ###    ####  ######  ########


class DataPersistanceService():
    """DataPersistenceService class provide access to underlying database storage
    via this class the application modules can create, read and update persistent objects
    """

    def __init__(self, username, password, dbname, host, port):
        """Constructor - create connection to RadPlanBio database
        """
        # DB logging
        isDbLoggingEnabled = True

        # Engine with connection string
        self.engine = create_engine('postgresql://' + username + ':' + password + '@' + host + ':' + port + '/' +  dbname, client_encoding='utf8', echo=isDbLoggingEnabled)

        # Session binned to DB engine - UnitOfWork design patter
        self.Session = scoped_session(
            sessionmaker(bind=self.engine)
        )

    def createOcDbConnection(self, ocusername, ocpassword, ocdbname, ochost, ocport):
        """Create connection to OpenClinica database
        """
        # DB logging
        isDbLoggingEnabled = True

        # Engine with connection string
        self.ocengine = create_engine("postgresql://" + ocusername + ":" + ocpassword + "@" + ochost + ":" + ocport + "/" +  ocdbname, client_encoding='utf8', echo=isDbLoggingEnabled)

        # Session binned to DB engine - UnitOfWork design patter
        self.ocSession = sessionmaker()
        self.ocSession.configure(bind=self.ocengine)

    def test(self):
        """Test DB engine connection
        """
        self.engine.execute("select 1").scalar()

 #######  ########  ######## ##    ##     ######  ##       #### ##    ## ####  ######     ###
##     ## ##     ## ##       ###   ##    ##    ## ##        ##  ###   ##  ##  ##    ##   ## ##
##     ## ##     ## ##       ####  ##    ##       ##        ##  ####  ##  ##  ##        ##   ##
##     ## ########  ######   ## ## ##    ##       ##        ##  ## ## ##  ##  ##       ##     ##
##     ## ##        ##       ##  ####    ##       ##        ##  ##  ####  ##  ##       #########
##     ## ##        ##       ##   ###    ##    ## ##        ##  ##   ###  ##  ##    ## ##     ##
 #######  ##        ######## ##    ##     ######  ######## #### ##    ## ####  ######  ##     ##

    def getAccountPasswordHash(self, session, username):
        """Get password hash for choosen OpenClinica user
        """
        selectPasswordHash = """select
            ua.passwd as PasswordHash
            from user_account ua
            where ua.user_name = :username"""

        conn = session.connection()
        result = conn.execute(text(selectPasswordHash),  {"username": username})

        for row in result:
            passwordHash = row[0]

        conn.close()

        return passwordHash

    def getOCStudyByIdentifier(self, session, identifier):
        """Get OC study by its identifier
        """
        studies = []

        sql = """SELECT s.study_id as id,
                s.unique_identifier as uniqueIdentifier,
                s.secondary_identifier as secondaryIdentifier,
                s.name as name
                FROM STUDY s
                LEFT JOIN STATUS st on st.status_id = s.status_id
                WHERE s.unique_identifier = :identifier"""

        conn = session.connection()
        results = conn.execute(text(sql),  {"identifier": identifier})

        for row in results:
            ocstudy = OCStudy()
 
            ocstudy.id = row[0]
            ocstudy.uniqueIdentifier = row[1]
            ocstudy.secondaryIdentifier = row[2]
            ocstudy.name = row[3]

            studies.append(ocstudy)

        if len(studies) == 1:
            return studies[0]
        else:
            return None

    def changeUserActiveStudy(self, session, username, newActiveStudyId):
        """Update active OC study of specified user
        """
        sql = """UPDATE USER_ACCOUNT
                SET active_study = :activeStudyId
                WHERE user_name = :username"""
 
        conn = session.connection()
        results = conn.execute(text(sql),  {"activeStudyId": newActiveStudyId, "username": username})

        print(results)

        return True

    def getCrfItemValueV2(self, session, studySiteOid, subjectPid, studyEventOid, studyEventRepeatKey, formOid, itemOid):
        """Get a value from OpenClinica eCRF field v2
        """
        value = ""

        # First get study id according to study site oid
        selectStudyId = """select
            s.study_id as StudyId
            from study s
            where s.oc_oid = :studySiteOid"""

        conn = session.connection()
        result = conn.execute(text(selectStudyId),  {'studySiteOid': studySiteOid})

        for row in result:
            studyId = row[0] # Just one record is here

        # Than get the Crf item
        # where StudyId,
        rawQuery = """select
            ss.study_subject_id,
            ss.label as SubjID,
            s.date_of_birth as BrthDat,
            s.gender as Sex,
            s.unique_identifier as SubjectPID,
            sed.study_event_definition_id as SEID,
            sed.name as SECode,
            sed.description as SEName,
            se.sample_ordinal as SERepeat,
            cv.crf_id as FormID,
            ec.crf_version_id as FormVersID,
            c.name as FormName,
            cv.name as VersionName,
            1 as FormRepeat,
            i.item_id as ItemID,
            i.name as ItemCode,
            id.ordinal as IGRepeat,
            i.description as Item,
            ifm.show_item as Visible,
            id.value as ItemValue,
            decode as ItemDecode

            from study_subject ss
            inner join subject s
                on ss.subject_id = s.subject_id
            inner join study_event se
                on ss.study_subject_id = se.study_subject_id
            inner join study_event_definition sed
                on se.study_event_definition_id = sed.study_event_definition_id
            inner join event_crf ec
                on se.study_event_id = ec.study_event_id
            inner join crf_version cv
                on ec.crf_version_id = cv.crf_version_id
            inner join crf c
                on cv.crf_id = c.crf_id
            inner join event_definition_crf edc
                on cv.crf_id = edc.crf_id
                and se.study_event_definition_id = edc.study_event_definition_id
            inner join item_form_metadata ifm
                on cv.crf_version_id = ifm.crf_version_id
            inner join item i
                on ifm.item_id = i.item_id
            left join item_data id
                on ec.event_crf_id = id.event_crf_id
                and i.item_id = id.item_id
            left join
            (
                select
                version_id as crf_version_id,
                response_set_id as set_id,
                label,
                options_values as value,
                options_text as decode
                from response_set
                where response_type_id = 3
                 union
                select
                  version_id as crf_version_id
                , response_set_id as set_id
                , label
                , trim (both from regexp_split_to_table(options_values, E',')) as value
                , trim (both from regexp_split_to_table(options_text, E',')) as decode
                from response_set
                where response_type_id = 6) cls
            on ifm.response_set_id = cls.set_id
            and ifm.crf_version_id = cls.crf_version_id
            and id.value = cls.value

            where ss.study_id = :studyId and
                s.unique_identifier = :subjectPid and
                sed.oc_oid = :studyEventOid and
                se.sample_ordinal = :studyEventRepeatKey and
                cv.oc_oid = :formOid and
                i.oc_oid = :itemOid
                order by
                ss.study_subject_id,
                sed.ordinal,
                se.sample_ordinal,
                edc.ordinal,
                id.ordinal,
                ifm.ordinal""" #c.oc_oid =  ... this is the same as version oid without v and number

        result = conn.execute(text(rawQuery), { "studyId" : studyId, "subjectPid" : subjectPid, "studyEventOid" : studyEventOid, "studyEventRepeatKey" : studyEventRepeatKey, "formOid" : formOid, "itemOid" : itemOid })

        for row in result:
            value = row[19] # ItemValue

        conn.close()

        return value

########  ######## ########    ###    ##     ## ##       ########       ###     ######   ######   #######  ##     ## ##    ## ########
##     ## ##       ##         ## ##   ##     ## ##          ##         ## ##   ##    ## ##    ## ##     ## ##     ## ###   ##    ##
##     ## ##       ##        ##   ##  ##     ## ##          ##        ##   ##  ##       ##       ##     ## ##     ## ####  ##    ##
##     ## ######   ######   ##     ## ##     ## ##          ##       ##     ## ##       ##       ##     ## ##     ## ## ## ##    ##
##     ## ##       ##       ######### ##     ## ##          ##       ######### ##       ##       ##     ## ##     ## ##  ####    ##
##     ## ##       ##       ##     ## ##     ## ##          ##       ##     ## ##    ## ##    ## ##     ## ##     ## ##   ###    ##
########  ######## ##       ##     ##  #######  ########    ##       ##     ##  ######   ######   #######   #######  ##    ##    ##

    def getAllDefaultAccounts(self, session):
        """Select all user default account objects
        """
        accounts = []

        for instance in session.query(DefaultAccount).order_by(DefaultAccount.id):
            accounts.append(instance)

        return accounts

    def getDefaultAccountByUsername(self, session, username):
        """Select one user default account object according to username
        """
        account = None
        query = session.query(DefaultAccount).filter(DefaultAccount.username == username)

        try:
            account = query.one()
        except MultipleResultsFound as e:
            print(e)
        except NoResultFound as e:
            print(e)

        return account

########     ###    ########  ######## ##    ## ######## ########      ######  #### ######## ########
##     ##   ## ##   ##     ##    ##    ###   ## ##       ##     ##    ##    ##  ##     ##    ##
##     ##  ##   ##  ##     ##    ##    ####  ## ##       ##     ##    ##        ##     ##    ##
########  ##     ## ########     ##    ## ## ## ######   ########      ######   ##     ##    ######
##        ######### ##   ##      ##    ##  #### ##       ##   ##            ##  ##     ##    ##
##        ##     ## ##    ##     ##    ##   ### ##       ##    ##     ##    ##  ##     ##    ##
##        ##     ## ##     ##    ##    ##    ## ######## ##     ##     ######  ####    ##    ########

    def getAllPartnerSites(self, session):
        """Select all partner sites from db
        """
        sites = []

        for instance in session.query(PartnerSite).order_by(PartnerSite.sitename):
            sites.append(instance)

        return sites

    def getAllPartnerExceptName(self, session, name):
        """Select all partner site except the specified one
        """
        sites = []
        query = session.query(PartnerSite).\
            filter(PartnerSite.sitename != name).\
            order_by(PartnerSite.sitename)

        for instance in query.all():
            sites.append(instance)

        return sites

    def getPartnerSiteByName(self, session, name):
        """Get partner site object according to name
        """
        site = None
        query = session.query(PartnerSite).filter(PartnerSite.sitename == name)

        try:
            site = query.one()
        except MultipleResultsFound as e:
            print(e)
        except NoResultFound as e:
            print(e)

        return site

    def getMySite(self, session):
        """Deprecated: Get my site
        """
        site = None
        query = session.query(PartnerSite).filter(PartnerSite.ismysite == True)

        try:
            site = query.one()
        except MultipleResultsFound as e:
            print(e)
        except NoResultFound as e:
            print(e)

        return site

 ######  ######## ##     ## ########  ##    ##
##    ##    ##    ##     ## ##     ##  ##  ##
##          ##    ##     ## ##     ##   ####
 ######     ##    ##     ## ##     ##    ##
      ##    ##    ##     ## ##     ##    ##
##    ##    ##    ##     ## ##     ##    ##
 ######     ##     #######  ########     ##

    def getAllStudies(self, session):
        """Get all RadPlaBio studies for database
        """
        studies = []

        for instance in session.query(Study):
            studies.append(instance)

        return studies

    def getStudyByOcIdentifier(self, session, ocidentifier):
        """Get RadPlanBio study according to ocidentifier
        """
        study = None

        query = session.query(Study).filter(Study.ocstudyidentifier == ocidentifier)

        try:
            study = query.one()
        except MultipleResultsFound as e:
            print(e)
        except NoResultFound as e:
            print(e)

        return study

 ######  ########  ########       ###    ##    ## ##    ##  #######  ########    ###    ######## ####  #######  ##    ##  ######
##    ## ##     ## ##            ## ##   ###   ## ###   ## ##     ##    ##      ## ##      ##     ##  ##     ## ###   ## ##    ##
##       ##     ## ##           ##   ##  ####  ## ####  ## ##     ##    ##     ##   ##     ##     ##  ##     ## ####  ## ##
##       ########  ######      ##     ## ## ## ## ## ## ## ##     ##    ##    ##     ##    ##     ##  ##     ## ## ## ##  ######
##       ##   ##   ##          ######### ##  #### ##  #### ##     ##    ##    #########    ##     ##  ##     ## ##  ####       ##
##    ## ##    ##  ##          ##     ## ##   ### ##   ### ##     ##    ##    ##     ##    ##     ##  ##     ## ##   ### ##    ##
 ######  ##     ## ##          ##     ## ##    ## ##    ##  #######     ##    ##     ##    ##    ####  #######  ##    ##  ######

    def getCrfFieldAnnotationsForStudy(self, session, studyid):
        """Get eCRF field annotations for study
        """
        crfFieldAnnotations = []

        for instance in session.query(CrfFieldAnnotation).filter(CrfFieldAnnotation.studyid == studyid):
            crfFieldAnnotations.append(instance)

        return crfFieldAnnotations

########  ########  ######  ######## ########  ##     ##  ######  ########
##     ##    ##    ##    ##    ##    ##     ## ##     ## ##    ##    ##
##     ##    ##    ##          ##    ##     ## ##     ## ##          ##
########     ##     ######     ##    ########  ##     ## ##          ##
##   ##      ##          ##    ##    ##   ##   ##     ## ##          ##
##    ##     ##    ##    ##    ##    ##    ##  ##     ## ##    ##    ##
##     ##    ##     ######     ##    ##     ##  #######   ######     ##

    def getAllRTStructs(self, session):
        """Select all RT-Structure objects
        """
        structs = []
        query = session.query(RTStruct)

        for instance in query.all():
            structs.append(instance)

        return structs

 ######   #######  ######## ######## ##      ##    ###    ########  ######## 
##    ## ##     ## ##          ##    ##  ##  ##   ## ##   ##     ## ##       
##       ##     ## ##          ##    ##  ##  ##  ##   ##  ##     ## ##       
 ######  ##     ## ######      ##    ##  ##  ## ##     ## ########  ######   
      ## ##     ## ##          ##    ##  ##  ## ######### ##   ##   ##       
##    ## ##     ## ##          ##    ##  ##  ## ##     ## ##    ##  ##       
 ######   #######  ##          ##     ###  ###  ##     ## ##     ## ########

    def getLatestSoftwareByName(self, session, name):
        """Get latest software
        """
        latestSoftware = None

        query = session.query(Software).\
            filter(Software.name == name).\
            filter(Software.latest == True)

        try:
            latestSoftware = query.one()
        except MultipleResultsFound as e:
            print(e)
        except NoResultFound as e:
            print(e)

        return latestSoftware