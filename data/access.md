# CloudDesk access policy, version 1

## ACCESS-01: Account recovery
A user with a lost MFA device can sign in using an unused recovery code. If no recovery code is available, the user must contact security@clouddesk.example for identity verification. A workspace admin cannot bypass MFA. Support never requests passwords, MFA codes, or recovery codes in a chat or email. The assistant cannot disable MFA or verify identities.

## ACCESS-02: Roles and SSO
Only a workspace owner can transfer ownership or cancel renewal. Admins can invite and remove members but cannot perform those owner-only actions. A billing admin can download invoices but cannot cancel renewal. SAML SSO is available only on Business. Enforcement requires a verified company domain and an owner to configure it. An owner locked out by SSO must use the security support recovery process; bypass is not guaranteed.
