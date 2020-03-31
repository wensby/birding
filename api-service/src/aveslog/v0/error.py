from enum import IntEnum


class ErrorCode(IntEnum):
  EMAIL_INVALID = 1
  EMAIL_TAKEN = 2
  USERNAME_TAKEN = 3
  CREDENTIALS_INCORRECT = 4
  AUTHORIZATION_REQUIRED = 5
  EMAIL_MISSING = 6
  OLD_PASSWORD_INCORRECT = 7
  ACCESS_TOKEN_INVALID = 8
  ACCESS_TOKEN_EXPIRED = 9
  PASSWORD_INVALID = 10
  ACCOUNT_MISSING = 11
  RATE_LIMIT_EXCEEDED = 12
  INVALID_ACCOUNT_REGISTRATION_TOKEN = 13
  VALIDATION_FAILED = 14
  INVALID_USERNAME_FORMAT = 15,
  INVALID_PASSWORD_FORMAT = 16,
  INVALID_LOCALE_CODE = 17,
  INVALID_FIELD_FORMAT = 18,
  SECONDARY_BIRDER_ID_INVALID = 19,
