"""

Implementation of the openEO error handling API
https://open-eo.github.io/openeo-api/errors/


To avoid brittle exception handling, we don't want to parse the error
spec at run time or dynamically generate openEO compliant exceptions.
Instead, we define a straightforward Python exception class for each
openEO error code.

To keep the implementation in sync with the spec, the following semi-automated
approach is followed:

- there are unit tests that do a compliance and health check of the exception
    classes (see test_errors.py). They will complain for example about
    missing exceptions or status code mismatches.
- executing this module directly will automatically generate source code
    for missing exceptions:

        python openeo_driver/errors.py

This approach also allows to customize certain exceptions a bit
where necessary or useful.

"""

import json
import re
import textwrap
from typing import List, Set
import uuid

from openeo_driver.specs import SPECS_ROOT


class OpenEOApiException(Exception):
    """
    Exception that wraps the fields/data necessary for OpenEO API compliant status/error handling

    see https://open-eo.github.io/openeo-api/errors/#json-error-object:

    required fields:
     - code: standardized textual openEO error code
     - message: human readable explanation

    optional:
     - id: unique identifier for referencing between API responses and server logs
     - url: link to resource that explains error/solutions
    """
    status_code = 500
    code = "Internal"
    message = "Unspecified Internal server error"
    _description = "Internal/generic error"
    _tags = ["General"]
    url = None

    def __init__(self, message=None, code=None, status_code=None, id=None, url=None):
        super().__init__(message or self.message)
        # (Standardized) textual openEO error code
        self.code = code or self.code
        # HTTP status code
        self.status_code = status_code or self.status_code
        self.id = id or str(uuid.uuid4())
        self.url = url or self.url

    def to_dict(self):
        """Generate OpenEO API compliant error dict to JSONify"""
        d = {"message": str(self), "code": self.code, "id": self.id}
        if self.url:
            d['url'] = self.url
        return d


# --- Begin of semi-autogenerated openEO exception classes ------------------------------------------------


class TokenInvalidException(OpenEOApiException):
    status_code = 403
    code = 'TokenInvalid'
    message = 'Session has expired.'
    _description = 'Authorization token invalid or expired.'
    _tags = ['Account Management']


class AuthenticationRequiredException(OpenEOApiException):
    status_code = 401
    code = 'AuthenticationRequired'
    message = 'Unauthorized.'
    _description = 'The client did not provide any authentication details for a resource requiring authentication or the provided authentication details are not correct.'
    _tags = ['Account Management']


class CredentialsInvalidException(OpenEOApiException):
    status_code = 403
    code = 'CredentialsInvalid'
    message = 'Credentials are not correct.'
    _description = None
    _tags = ['Account Management']


class AuthenticationSchemeInvalidException(OpenEOApiException):
    status_code = 403
    code = 'AuthenticationSchemeInvalid'
    message = 'Authentication method not supported.'
    _description = 'Invalid authentication scheme (e.g. Bearer).'
    _tags = ['Account Management']


class CollectionNotFoundException(OpenEOApiException):
    status_code = 404
    code = 'CollectionNotFound'
    message = "Collection '{identifier}' does not exist."
    _description = 'The requested collection does not exist.'
    _tags = ['EO Data Discovery', 'Processes']

    def __init__(self, collection_id: str):
        super().__init__(message=self.message.format(identifier=collection_id))


class FileLockedException(OpenEOApiException):
    status_code = 400
    code = 'FileLocked'
    message = "File '{file}' is locked."
    _description = 'The file is locked by a running job or another process.'
    _tags = ['File Management']

    def __init__(self, file: str):
        super().__init__(message=self.message.format(file=file))


class FileSizeExceededException(OpenEOApiException):
    status_code = 400
    code = 'FileSizeExceeded'
    message = 'File size it too large. Maximum file size: {size}'
    _description = 'File exceeds allowed maximum file size.'
    _tags = ['File Management']

    def __init__(self, size: str):
        super().__init__(message=self.message.format(size=size))


class FilePathInvalidException(OpenEOApiException):
    status_code = 400
    code = 'FilePathInvalid'
    message = 'File path is invalid.'
    _description = 'The specified path is invalid or not accessible. Path could contain invalid characters, an invalid user ID or point to an existing folder or a location outside of the user folder.'
    _tags = ['File Management']


class FileTypeInvalidException(OpenEOApiException):
    status_code = 400
    code = 'FileTypeInvalid'
    message = 'File type not allowed. Allowed file types: {types}'
    _description = 'File format, file extension or media (MIME) type is not allowed.'
    _tags = ['File Management']

    def __init__(self, types: str):
        super().__init__(message=self.message.format(types=types))


class FileOperationUnsupportedException(OpenEOApiException):
    status_code = 400
    code = 'FileOperationUnsupported'
    message = 'Operation is only supported for files.'
    _description = 'The specified path is not a file and the operation is only supported for files. Path is likely a directory.'
    _tags = ['File Management']


class ContentTypeInvalidException(OpenEOApiException):
    status_code = 400
    code = 'ContentTypeInvalid'
    message = 'The media type is not supported. Allowed: {types}'
    _description = 'The specified media (MIME) type used in the Content-Type header is not allowed.'
    _tags = ['File Management', 'General']

    def __init__(self, types: str):
        super().__init__(message=self.message.format(types=types))


class StorageFailureException(OpenEOApiException):
    status_code = 500
    code = 'StorageFailure'
    message = 'Unable to store file(s).'
    _description = "Server couldn't store file(s) due to server-side reasons."
    _tags = ['File Management', 'Job Management']


class StorageQuotaExceededException(OpenEOApiException):
    status_code = 400
    code = 'StorageQuotaExceeded'
    message = 'Insufficient Storage.'
    _description = 'The storage quota has been exceeded by the user.'
    _tags = ['File Management', 'Job Management']


class FileNotFoundException(OpenEOApiException):
    status_code = 404
    code = 'FileNotFound'
    message = "File '{file}' does not exist."
    _description = 'The requested file does not exist.'
    _tags = ['File Management', 'Processes']

    def __init__(self, filename: str):
        super().__init__(message=self.message.format(file=filename))


class FileContentInvalidException(OpenEOApiException):
    status_code = 400
    code = 'FileContentInvalid'
    message = 'File content is invalid.'
    _description = 'The content of the file is invalid.'
    _tags = ['File Management', 'Processes']


class InternalException(OpenEOApiException):
    status_code = 500
    code = 'Internal'
    message = 'Server error: {message}'
    _description = 'An internal server error with a proprietary message.'
    _tags = ['General']

    def __init__(self, message: str):
        super().__init__(message=self.message.format(message=message))


class InfrastructureMaintenanceException(OpenEOApiException):
    status_code = 503
    code = 'InfrastructureMaintenance'
    message = 'Service is not available at the moment due to maintenance work. Please try again later.'
    _description = 'Service is currently not available, but the infrastructure is currently undergoing maintenance work.'
    _tags = ['General']


class InfrastructureBusyException(OpenEOApiException):
    status_code = 503
    code = 'InfrastructureBusy'
    message = 'Service is not available at the moment due to overloading. Please try again later.'
    _description = "Service is generally available, but the infrastructure can't handle it at the moment as too many requests are processed."
    _tags = ['General']


class FeatureUnsupportedException(OpenEOApiException):
    status_code = 501
    code = 'FeatureUnsupported'
    message = 'Feature not supported.'
    _description = 'The back-end responds with this error whenever an endpoint is specified in the openEO API, but is not supported.'
    _tags = ['General']


class NotFoundException(OpenEOApiException):
    status_code = 404
    code = 'NotFound'
    message = 'Resource not found.'
    _description = "To be used if the requested resource does not exist. Note: Unsupported endpoints MUST send an 'FeatureUnsupported' error. There are also specialized errors for missing jobs (JobNotFound), files (FileNotFound), etc."
    _tags = ['General']


class RequestTimeoutException(OpenEOApiException):
    status_code = 408
    code = 'RequestTimeout'
    message = 'Request timed out.'
    _description = 'The request took too long and timed out.'
    _tags = ['General', 'Job Management']


class ProcessGraphComplexityException(OpenEOApiException):
    status_code = 400
    code = 'ProcessGraphComplexity'
    message = 'The process graph is too complex for for synchronous processing. Please use a batch job instead.'
    _description = 'The process graph is too complex for synchronous processing and likely to time out. Please use a batch job instead.'
    _tags = ['Job Management']


class FormatUnsuitableException(OpenEOApiException):
    status_code = 400
    code = 'FormatUnsuitable'
    message = "Data can't be transformed into the requested output format."
    _description = None
    _tags = ['Job Management']


class FormatArgumentUnsupportedException(OpenEOApiException):
    status_code = 400
    code = 'FormatArgumentUnsupported'
    message = "Output format argument '{argument}' is not supported."
    _description = None
    _tags = ['Job Management']

    def __init__(self, argument: str):
        super().__init__(message=self.message.format(argument=argument))


class JobNotFinishedException(OpenEOApiException):
    status_code = 400
    code = 'JobNotFinished'
    message = 'Job has not finished computing the results yet. Please try again later.'
    _description = None
    _tags = ['Job Management']


class JobLockedException(OpenEOApiException):
    status_code = 400
    code = 'JobLocked'
    message = 'Job is locked due to a queued or running batch computation.'
    _description = "The job is currently locked due to a running batch computation and can't be modified meanwhile."
    _tags = ['Job Management']


class FormatUnsupportedException(OpenEOApiException):
    status_code = 400
    code = 'FormatUnsupported'
    message = 'Output format not supported.'
    _description = None
    _tags = ['Job Management']


class JobNotStartedException(OpenEOApiException):
    status_code = 400
    code = 'JobNotStarted'
    message = "Job hasn't been started yet."
    _description = 'Job has not been queued or started yet or was canceled and not restarted by the user.'
    _tags = ['Job Management']


class FormatArgumentInvalidException(OpenEOApiException):
    status_code = 400
    code = 'FormatArgumentInvalid'
    message = "The output format argument '{argument}' is invalid: {reason}"
    _description = None
    _tags = ['Job Management']

    def __init__(self, argument: str, reason: str):
        super().__init__(message=self.message.format(argument=argument, reason=reason))


class PropertyNotEditableException(OpenEOApiException):
    status_code = 400
    code = 'PropertyNotEditable'
    message = "Property '{property}' is read-only."
    _description = "For PATCH requests: The specified parameter can't be updated. It is read-only."
    _tags = ['Job Management', 'Process Graph Management', 'Secondary Services Management']

    def __init__(self, property: str):
        super().__init__(message=self.message.format(property=property))


class ProcessGraphMissingException(OpenEOApiException):
    status_code = 400
    code = 'ProcessGraphMissing'
    message = 'No valid process graph specified.'
    _description = None
    _tags = ['Job Management', 'Process Graph Management', 'Secondary Services Management']


class NoDataForUpdateException(OpenEOApiException):
    status_code = 400
    code = 'NoDataForUpdate'
    message = 'No valid data specified to be updated.'
    _description = 'For PATCH requests: No valid data specified at all.'
    _tags = ['Job Management', 'Process Graph Management', 'Secondary Services Management']


class JobNotFoundException(OpenEOApiException):
    status_code = 404
    code = 'JobNotFound'
    message = "The job '{identifier}' does not exist."
    _description = 'The requested job does not exist.'
    _tags = ['Job Management', 'Processes']

    def __init__(self, job_id: str):
        super().__init__(message=self.message.format(identifier=job_id))


class BillingPlanInvalidException(OpenEOApiException):
    status_code = 400
    code = 'BillingPlanInvalid'
    message = 'The billing plan is not valid.'
    _description = 'The billing plan is not on the list of available plans.'
    _tags = ['Job Management', 'Secondary Services Management']


class PaymentRequiredException(OpenEOApiException):
    status_code = 402
    code = 'PaymentRequired'
    message = 'Payment required.'
    _description = 'The budget required to fulfil the request are insufficient.'
    _tags = ['Job Management', 'Secondary Services Management']


class BudgetInvalidException(OpenEOApiException):
    status_code = 400
    code = 'BudgetInvalid'
    message = 'The budget is too low.'
    _description = 'The budget is too low as it is either smaller than or equal to 0 or below the costs.'
    _tags = ['Job Management', 'Secondary Services Management']


class ProcessGraphNotFoundException(OpenEOApiException):
    status_code = 404
    code = 'ProcessGraphNotFound'
    message = "Process graph '{identifier}' does not exist."
    _description = 'The requested process graph does not exist.'
    _tags = ['Process Graph Management']

    def __init__(self, process_graph_id: str):
        super().__init__(message=self.message.format(identifier=process_graph_id))


class ProcessArgumentInvalidException(OpenEOApiException):
    status_code = 400
    code = 'ProcessArgumentInvalid'
    message = "The argument '{argument}' in process '{process}' is invalid: {reason}"
    _description = None
    _tags = ['Processes']

    def __init__(self, argument: str, process: str, reason: str):
        super().__init__(message=self.message.format(argument=argument, process=process, reason=reason))


class ProcessUnsupportedException(OpenEOApiException):
    status_code = 400
    code = 'ProcessUnsupported'
    message = "Process '{process}' is not supported."
    _description = None
    _tags = ['Processes']

    def __init__(self, process: str):
        super().__init__(message=self.message.format(process=process))


class CoordinateOutOfBoundsException(OpenEOApiException):
    status_code = 400
    code = 'CoordinateOutOfBounds'
    message = 'Coordinate is out of bounds.'
    _description = None
    _tags = ['Processes']


class CRSInvalidException(OpenEOApiException):
    status_code = 400
    code = 'CRSInvalid'
    message = "CRS '{crs}' is invalid."
    _description = 'Invalid or unsupported CRS specified.'
    _tags = ['Processes']

    def __init__(self, crs: str):
        super().__init__(message=self.message.format(crs=crs))


class ProcessArgumentRequiredException(OpenEOApiException):
    status_code = 400
    code = 'ProcessArgumentRequired'
    message = "Process '{process}' requires argument '{argument}'."
    _description = None
    _tags = ['Processes']

    def __init__(self, process: str, argument: str):
        super().__init__(message=self.message.format(process=process, argument=argument))


class ProcessArgumentUnsupportedException(OpenEOApiException):
    status_code = 400
    code = 'ProcessArgumentUnsupported'
    message = "Process '{process}' does not support argument '{argument}'."
    _description = None
    _tags = ['Processes']

    def __init__(self, process: str, argument: str):
        super().__init__(message=self.message.format(process=process, argument=argument))


class ProcessParameterMissingException(OpenEOApiException):
    status_code = 400
    code = 'ProcessParameterMissing'
    message = "The process parameter '{parameter}' must be specified."
    _description = None
    _tags = ['Processes']

    def __init__(self, parameter: str):
        super().__init__(message=self.message.format(parameter=parameter))


class ServiceArgumentUnsupportedException(OpenEOApiException):
    status_code = 400
    code = 'ServiceArgumentUnsupported'
    message = "Secondary service argument '{argument}' is not supported."
    _description = None
    _tags = ['Secondary Services Management']

    def __init__(self, argument: str):
        super().__init__(message=self.message.format(argument=argument))


class ServiceUnsupportedException(OpenEOApiException):
    status_code = 400
    code = 'ServiceUnsupported'
    message = 'Secondary service type is not supported.'
    _description = None
    _tags = ['Secondary Services Management']


class ServiceArgumentRequiredException(OpenEOApiException):
    status_code = 400
    code = 'ServiceArgumentRequired'
    message = "Required secondary service argument '{argument}' is missing."
    _description = None
    _tags = ['Secondary Services Management']

    def __init__(self, argument: str):
        super().__init__(message=self.message.format(argument=argument))


class ServiceNotFoundException(OpenEOApiException):
    status_code = 404
    code = 'ServiceNotFound'
    message = "Service '{identifier}' does not exist."
    _description = 'The requested secondary service does not exist.'
    _tags = ['Secondary Services Management']

    def __init__(self, service_id: str):
        super().__init__(message=self.message.format(identifier=service_id))


class ServiceArgumentInvalidException(OpenEOApiException):
    status_code = 400
    code = 'ServiceArgumentInvalid'
    message = "The secondary service argument '{argument}' is invalid: {reason}"
    _description = None
    _tags = ['Secondary Services Management']

    def __init__(self, argument: str, reason: str):
        super().__init__(message=self.message.format(argument=argument, reason=reason))


# --- End of semi-autogenerated openEO exception classes ------------------------------------------------


class OpenEOApiErrorSpecHelper:
    """
    Helper class around OpenEO API error handling spec to support automated
    generation of Python exception classes
    """
    _placeholder_regex = re.compile(r"{(\w+)}")

    def __init__(self, spec: dict = None):
        if spec is None:
            with (SPECS_ROOT / 'openeo-api/1.0/errors.json').open('r', encoding='utf-8') as f:
                spec = json.load(f)
        self._spec = spec

    def get(self, error_code: str) -> dict:
        return self._spec[error_code]

    def get_error_codes(self) -> List[str]:
        return list(self._spec.keys())

    def generate_exception_class(self, error_code: str) -> str:
        """Generate source code for given OpenEO error code"""
        spec = self._spec[error_code]
        message = spec["message"]
        src = textwrap.dedent("""\
            class {code}Exception({parent}):
                status_code = {status}
                code = {code!r}
                message = {message!r}
                _description = {description!r}
                _tags = {tags!r}
            """.format(
            code=error_code, parent=OpenEOApiException.__name__,
            status=spec["http"],
            message=message,
            description=spec["description"],
            tags=sorted(spec["tags"]),
        ))
        placeholders = self.extract_placeholders(message)
        if placeholders:
            init = textwrap.dedent("""\
                def __init__(self, {args}):
                    super().__init__(message=self.message.format({format_args}))
            """.format(
                args=", ".join("{p}: str".format(p=p) for p in placeholders),
                format_args=", ".join("{p}={p}".format(p=p) for p in placeholders)
            ))
            src += "\n" + textwrap.indent(init, prefix=" " * 4)
        return src

    @classmethod
    def extract_placeholders(cls, message) -> Set[str]:
        return set(cls._placeholder_regex.findall(message))


if __name__ == '__main__':
    # Print suggested exception class implementations for missing errors
    spec_helper = OpenEOApiErrorSpecHelper()

    implemented_codes = [
        v.code for v in globals().values()
        if isinstance(v, type) and issubclass(v, OpenEOApiException)
    ]
    unimplemented = set(spec_helper.get_error_codes()).difference(implemented_codes)
    # Sort on tag
    unimplemented = sorted(unimplemented, key=lambda code: sorted(spec_helper.get(code)["tags"]))

    if unimplemented:
        for code in unimplemented:
            print("### Found {c} unimplemented openEO error codes. Suggested implementation:".format(
                c=len(unimplemented)))
            print(spec_helper.generate_exception_class(code) + "\n")
    else:
        print("###No unimplemented openEO error codes.")
