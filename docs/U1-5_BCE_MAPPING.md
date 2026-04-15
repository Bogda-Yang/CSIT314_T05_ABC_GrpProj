# U1-5 BCE Mapping

This version lists only real method/function definition lines.

Scope:

- `U1 Register`
- `U2 Login`
- `U3 Logout`
- `U4 Update Profile`
- `U5 Change Password`

Notes:

- Only actual `def` or `function` definitions are listed.
- Conceptual BCE boundary actions such as `EnterUsername()` or `DisplayLoginResult()` are not repeated unless there is a real code definition for them.

## U1 Register

| BCE Class | Method definitions |
|---|---|
| `RegisterPage` | `auth_page()` `routers/user.py:99`, `handleRegister()` `static/auth.js:204`, `handleSendCode()` `static/auth.js:263` |
| `AuthController` | `ValidateRegistrationInput()` `services/user_service.py:430`, `CheckEmail()` `services/user_service.py:451`, `SendVerificationEmail()` `services/user_service.py:456`, `VerifyEmailAddress()` `services/user_service.py:460`, `RequestVerificationCode()` `services/user_service.py:464`, `ValidationVerificationCode()` `services/user_service.py:472`, `CreateAccount()` `services/user_service.py:476` |
| `UserAccount` | `CreateUser()` `models/user.py:23`, `SaveUser()` `models/user.py:34`, `CheckEmail()` `models/user.py:42` |
| `EmailVerification` | `GenerateCode()` `services/user_service.py:350`, `StoreCode()` `services/user_service.py:354`, `CheckCode()` `services/user_service.py:375` |

## U2 Login

| BCE Class | Method definitions |
|---|---|
| `LoginPage` | `auth_page()` `routers/user.py:99`, `handleLogin()` `static/auth.js:177` |
| `AuthController` | `ValidateCredentials()` `services/user_service.py:506`, `CreateSession()` `services/user_service.py:513`, `Login()` `services/user_service.py:530` |
| `UserAccount` | `GetUserByEmail()` `models/user.py:38`, `CheckPassword()` `models/user.py:46` |
| `UserSession` | `CreateSession()` `models/user.py:208`, `StoreSession()` `models/user.py:219` |
| `AuthenticationToken` | `CreateToken()` `models/user.py:244`, `FindToken()` `models/user.py:255`, `RevokeToken()` `models/user.py:261` |

## U3 Logout

| BCE Class | Method definitions |
|---|---|
| `DashboardPage` | `logout()` `routers/user.py:118` |
| `SessionController` | `RequestLogout()` `services/user_service.py:538`, `Logout()` `services/user_service.py:542`, `TerminateSession()` `services/user_service.py:548`, `ClearAuthentication()` `services/user_service.py:564` |
| `UserSession` | `FindSession()` `models/user.py:223`, `InvalidateSession()` `models/user.py:229` |
| `AuthenticationToken` | `FindToken()` `models/user.py:255`, `RevokeToken()` `models/user.py:261` |

## U4 Update Profile

| BCE Class | Method definitions |
|---|---|
| `ProfilePage` | `profile_page()` `routers/user.py:34` |
| `ProfileController` | `ViewCurrentProfile()` `services/user_service.py:570`, `GetProfile()` `services/user_service.py:574`, `ValidateProfileInput()` `services/user_service.py:605`, `UpdateProfile()` `services/user_service.py:637`, `SaveProfileChanges()` `services/user_service.py:677` |
| `UserProfile` | `GetProfileDetails()` `models/user.py:92`, `UpdateProfileDetails()` `models/user.py:96`, `SaveProfile()` `models/user.py:132` |
| `UserAccount` | `GetUserAccount()` `models/user.py:51` |

## U5 Change Password

| BCE Class | Method definitions |
|---|---|
| `ChangePasswordPage` | `settings_page()` `routers/user.py:73` |
| `PasswordController` | `ValidationCurrentPassword()` `services/user_service.py:745`, `ValidateNewPassword()` `services/user_service.py:756`, `ValidatePasswordPolicy()` `services/user_service.py:784`, `SendPasswordChangeNotification()` `services/user_service.py:799`, `UpdatePassword()` `services/user_service.py:808` |
| `UserProfile` | `GetPasswordHash()` `models/user.py:158`, `UpdatePasswordHash()` `models/user.py:162` |
| `PasswordHistory` | `StorePasswordHistory()` `models/user.py:178`, `GetPreviousPasswords()` `models/user.py:189` |
