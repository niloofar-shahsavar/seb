| Rule   | Checks                                                           |
| ------ | ---------------------------------------------------------------- |
| **R1** | Is the `asset_type` allowed?                                     |
| **R2** | If it's an equity: is it listed on an approved exchange?         |
| **R3** | If it's a fund: is its ISIN in `approved_funds`?                 |
| **R4** | If it's a bond: is its rating at least `BBB-`?                   |
| **R5** | Is the instrument issued by the insurer's own group, e.g. `SEB`? |
