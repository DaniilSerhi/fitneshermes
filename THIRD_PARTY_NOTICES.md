# Third-party components

| Component | Relationship to this project | Distribution here |
|---|---|---|
| Nous Research Hermes Agent | Runtime for the personal assistant | Runtime omitted; existing MIT license notice preserved |
| Python standard library | Public demo execution and tests | No interpreter or library copies bundled |
| FatSecret | Format of the nutrition export consumed by the parser | No real exports or proprietary datasets; invented CSV only |
| Garmin Connect / garminconnect | Wearable integration in the personal deployment | No SDK, authentication state or real observations bundled |
| OpenRouter and hosted model providers | Model access in the personal deployment | No SDK copies, weights or generated personal conversations |
| Telegram / python-telegram-bot | Messaging in the personal deployment | No bot runtime or tokens bundled |
| GitHub Actions checkout/setup-python | Referenced by the optional CI workflow | No action source copied |

Hermes attribution: Copyright (c) 2025 Nous Research. See [the preserved license](licenses/HERMES-MIT.txt).

Product names describe integration context. No affiliation, endorsement or ownership of those products is implied.
