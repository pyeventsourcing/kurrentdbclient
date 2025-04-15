from opentelemetry.semconv._incubating.attributes import db_attributes
from opentelemetry.semconv.attributes import exception_attributes, server_attributes


class Attributes:
    DB_OPERATION = db_attributes.DB_OPERATION
    DB_SYSTEM = db_attributes.DB_SYSTEM
    DB_USER = db_attributes.DB_USER
    EVENTSTOREDB_STREAM = "db.kurrentdb.stream"
    EVENTSTOREDB_SUBSCRIPTION_ID = "db.kurrentdb.subscription.id"
    EVENTSTOREDB_EVENT_ID = "db.kurrentdb.event.id"
    EVENTSTOREDB_EVENT_TYPE = "db.kurrentdb.event.type"
    EXCEPTION_ESCAPED = exception_attributes.EXCEPTION_ESCAPED
    EXCEPTION_MESSAGE = exception_attributes.EXCEPTION_MESSAGE
    EXCEPTION_STACKTRACE = exception_attributes.EXCEPTION_STACKTRACE
    EXCEPTION_TYPE = exception_attributes.EXCEPTION_TYPE
    SERVER_ADDRESS = server_attributes.SERVER_ADDRESS
    SERVER_PORT = server_attributes.SERVER_PORT
