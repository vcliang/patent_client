import datetime

from yankee.json.schema import RegexSchema, Schema, ZipSchema
from yankee.json.schema import fields as f

from patent_client.util.claims.parser import ClaimsParser

from ..util import html_to_text
from .shared import DocumentStructureSchema


def parse_claims(html):
    text = html_to_text(html)
    if text:
        try:
            return ClaimsParser().parse(text)
        except Exception:
            return list()
    return list()


class DocumentSchema(Schema):
    abstract_html = f.String("abstractHtml")
    government_interest = f.String("governmentInterest")
    background_html = f.String("backgroundTextHtml")
    brief_html = f.String("briefHtml")
    description_html = f.String("descriptionHtml")
    claim_statement = f.String("claimStatement")
    claims_html = f.String("claimsHtml")
    claims = f.String("claimsHtml", formatter=parse_claims)


class UsReferenceSchema(ZipSchema):
    publication_number = f.String("urpn")
    # us_class = f.String("usRefClassification")
    # cpc_class = f.String("usRefCpcClassification")
    # group = f.String("usRefGroup")
    pub_month = f.Date(
        "usRefIssueDate",
        dt_converter=lambda s: datetime.datetime(year=int(s[:4]), month=int(s[4:6]), day=1),
    )
    patentee_name = f.String("usRefPatenteeName")
    cited_by_examiner = f.Boolean("usRefGroup", true_func=lambda s: "examiner" in s)


class ForeignReferenceSchema(ZipSchema):
    citation_classification = f.String("foreignRefCitationClassification")
    citation_cpc = f.String("foreignRefCitationCpc")
    country_code = f.String("foreignRefCountryCode")
    # group = f.String("foreignRefGroup")
    patent_number = f.String("foreignRefPatentNumber")
    pub_month = f.Date(
        "foreignRefPubDate",
        dt_converter=lambda s: datetime.datetime(year=int(s[:4]), month=int(s[4:6]), day=1),
    )
    cited_by_examiner = f.Boolean("foreignRefGroup", true_func=lambda s: "examiner" in s)


class NplReferenceSchema(RegexSchema):
    __regex__ = r"(?P<citation>.*)(?P<cited_by_examiner>cited by (applicant|examiner).?$)"
    citation = f.String()
    cited_by_examiner = f.Bool(true_func=lambda s: "examiner" in s)


class RelatedApplicationSchema(ZipSchema):
    child_patent_country = f.String("relatedApplChildPatentCountry")
    child_patent_number = f.String("relatedApplChildPatentNumber")
    country_code = f.String("relatedApplCountryCode")
    filing_date = f.Date("relatedApplFilingDate")
    number = f.String("relatedApplNumber")
    parent_status_code = f.String("relatedApplParentStatusCode")
    patent_issue_date = f.Date("relatedApplPatentIssueDate")
    patent_number = f.String("relatedApplPatentNumber")


class InventorSchema(ZipSchema):
    name = f.String("inventorsName")
    city = f.String("inventorCity")
    country = f.String("inventorCountry")
    postal_code = f.String("inventorPostalCode")
    state = f.String("inventorState")


class ApplicantSchema(ZipSchema):
    city = f.String("applicantCity")
    country = f.String("applicantCountry")
    # group = f.String("applicantGroup")
    name = f.String("applicantName")
    state = f.String("applicantState")
    zip_code = f.String("applicantZipCode")
    authority_type = f.String("applicantAuthorityType")


class AssigneeSchema(ZipSchema):
    city = f.String("assigneeCity")
    country = f.String("assigneeCountry")
    name = f.String("assigneeName")
    postal_code = f.String("assigneePostalCode")
    state = f.String("assigneeState")
    type_code = f.String("assigneeTypeCode")


class CpcCodeSchema(RegexSchema):
    __regex__ = r"(?P<cpc_class>.{4})(?P<cpc_subclass>[^ ]+) (?P<version>\d{8})"
    cpc_class = f.Str()
    cpc_subclass = f.Str()
    version = f.Date()


class IntlCodeSchema(RegexSchema):
    __regex__ = r"(?P<intl_class>.{4})(?P<intl_subclass>[^ ]+) (?P<version>\d{8})"
    intl_class = f.Str()
    intl_subclass = f.Str()
    version = f.Date()


class ForeignPriorityApplicationSchema(ZipSchema):
    country = f.Str("priorityClaimsCountry")
    app_filing_date = f.Date("priorityClaimsDate")
    app_number = f.Str("priorityClaimsDocNumber")


class PublicSearchDocumentSchema(Schema):
    guid = f.String("guid")
    publication_number = f.String("pubRefDocNumber")
    publication_date = f.Date("datePublished")

    appl_id = f.String("applicationNumber")
    patent_title = f.String("inventionTitle")
    app_filing_date = f.Date("applicationFilingDate.0")
    application_type = f.String("applicationRefFilingType")
    family_identifier_cur = f.Integer("familyIdentifierCur")
    related_apps = RelatedApplicationSchema(data_key=False)
    foreign_priority = ForeignPriorityApplicationSchema(data_key=False)
    type = f.String("type")

    # Parties
    inventors = InventorSchema(data_key=False)
    inventors_short = f.String("inventorsShort")
    applicants = ApplicantSchema(data_key=False)
    assignees = AssigneeSchema(data_key=False)

    group_art_unit = f.String("examinerGroup")
    primary_examiner = f.String("primaryExaminer")
    assistant_examiner = f.List(f.String, "assistantExaminer")
    legal_firm_name = f.List(f.String, "legalFirmName")
    attorney_name = f.List(f.String, "attorneyName")

    # Text Data
    document = DocumentSchema(data_key=False)
    document_structure = DocumentStructureSchema(data_key=False)

    # Image Data
    image_file_name = f.String("imageFileName")
    image_location = f.String("imageLocation")

    # Metadata
    composite_id = f.String("compositeId")
    database_name = f.String("databaseName")
    derwent_week_int = f.Integer("derwentWeekInt")

    # References Cited
    us_references = UsReferenceSchema(data_key=False)
    foreign_references = ForeignReferenceSchema(data_key=False)
    npl_references = f.DelimitedString(NplReferenceSchema, "otherRefPub.0", delimeter="<br />")

    # Classifications
    cpc_inventive = f.List(CpcCodeSchema)
    cpc_additional = f.List(CpcCodeSchema)

    intl_class_issued = f.DelimitedString(f.String, "ipcCodeFlattened", delimeter=";")
    intl_class_current_primary = f.List(IntlCodeSchema, "curIntlPatentClassificationPrimary")
    intl_class_currrent_secondary = f.List(IntlCodeSchema, "curIntlPatentClassificationSecondary")

    us_class_current = f.DelimitedString(f.Str(), "uspcFullClassificationFlattened", delimeter=";")
    us_class_issued = f.List(f.Str, "issuedUsClassificationFull")

    field_of_search_us = f.List(f.Str(), "fieldOfSearchClassSubclassHighlights")
    field_of_search_cpc = f.List(f.Str(), "fieldOfSearchCpcClassification")
