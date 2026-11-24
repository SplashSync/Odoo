# V1 field ids → catalog templates (first pass)

> Gen 3 reality per object: `python3 tools/fields_report.py <ObjectType>` (V1 manifest vs `splash.json`).

> Generated from the V1 manifest `docs/plan/v1-legacy-manifest.json` and the catalog embedded in splashpy 3.0
> (`src/splashpy/contracts/data/templates.json`, 232 templates), matched on **itemtype + itemprop**.
> Warning: `splash.json` was generated on an old V1 (Odoo 12 era field names: `date_invoice`, `number`,
> `customer`...). The live 18.0 manifest must be regenerated (work item M1-02) before this table is final.
> **Rule: field ids are kept.** Templates only bring type, microdata, names and flags.
Explicit fields matched on microdata: **113 / 156**. Unmatched ones need a manual choice (MCP Toolkit).


## ThirdParty

V1 manifest: 88 fields, of which ~66 auto-discovered from `fields_get()` (group "Others", see end of section).

| Field id (kept) | V1 type | R/W | V1 microdata | Template candidate(s) |
|---|---|---|---|---|
| `active` | bool | W | organization/active | `ThirdParty.Flags.Active` |
| `city` | varchar | W | postaladdress/addressLocality | `Address.PostalAddress.Locality` |
| `company_type` | varchar | W | product/Company Type | **none** — keep custom |
| `create_date` | datetime | RO | datafeeditem/dateCreated | `Common.Audit.DateCreated` |
| `customer` | bool | W | organization/customer | `ThirdParty.Flags.Customer` |
| `email` | email | W | contactpoint/email | `Address.Contact.Email`, `ThirdParty.Core.Email` |
| `is_company` | bool | W | product/Is a Company | **none** — keep custom |
| `phone` | phone | W | person/telephone | `Address.Contact.Phone`, `ThirdParty.Core.MobilePhone` |
| `street` | varchar | W | postaladdress/streetAddress | `Address.PostalAddress.StreetAddress` |
| `supplier` | bool | W | organization/supplier | `ThirdParty.Flags.Supplier` |
| `type` | varchar | W | product/Address Type | **none** — keep custom |
| `vat` | varchar | W | product/Tax ID | **none** — keep custom |
| `website` | url | W | organization/url | `ThirdParty.Profile.Website` |
| `write_date` | datetime | RO | datafeeditem/dateModified | `Common.Audit.DateModified` |
| `zip` | varchar | W | postaladdress/postalCode | `Address.PostalAddress.PostalCode` |
| `country_code` | country | W | postaladdress/addressCountry | `Address.PostalAddress.CountryCode` |
| `country_name` | varchar | W | postaladdress/addressCountryName | `Address.PostalAddress.CountryName` |
| `state_id` | state | W | postaladdress/addressRegion | `Address.PostalAddress.RegionCode` |
| `legal` | varchar | RW | organization/legalName | `Accounting.Supplier.SupplierName`, `Address.Contact.Name`, `ThirdParty.Core.Name` |
| `last` | varchar | W | person/givenName | `Address.Contact.Firstname`, `ThirdParty.Core.Lastname` |
| `first` | varchar | W | person/familyName | `Address.Contact.Lastname`, `ThirdParty.Core.Firstname` |
| `parent_id` | objectid::ThirdParty | W | organization/ID | `Accounting.Core.ThirdParty`, `Address.Core.ThirdParty` |
| `user_id` | — | — | not in old manifest | to check on 18.0 |
| `user_email` | — | — | not in old manifest | to check on 18.0 |
| `team_id` | — | — | not in old manifest | to check on 18.0 |
| `company` | — | — | not in old manifest | to check on 18.0 |

Auto-discovered fields (66): `__last_update`, `activity_date_deadline`, `activity_state`, `activity_summary`, `additional_info`, `bank_account_count`, `barcode`, `color`, `comment`, `commercial_company_name`, `company_name`, `contact_address`, `contracts_count`, `credit`, `credit_limit`, `date`, `debit`, `debit_limit`, `display_name`, `email_formatted`, `employee`, `function`, `has_unreconciled_entries`, `im_status`, `image`, `invoice_warn`, `invoice_warn_msg`, `is_blacklisted`, `journal_item_count`, `lang`, `last_time_entries_checked`, `message_attachment_count`, `message_bounce`, `message_has_error`, `message_has_error_counter`, `message_is_follower`, `message_needaction`, `message_needaction_counter`, `message_unread`, `message_unread_counter`, `mobile`, `name`, `parent_name`, `partner_gid`, `partner_share`, `payment_token_count`, `picking_warn`, `picking_warn_msg`, `purchase_order_count`, `purchase_warn`, `purchase_warn_msg`, `ref`, `sale_order_count`, `sale_warn`, `sale_warn_msg`, `signup_expiration`, `signup_token`, `signup_type`, `signup_url`, `signup_valid`, `street2`, `supplier_invoice_count`, `total_invoiced`, `trust`, `tz`, `tz_offset`

## Order

V1 manifest: 89 fields, of which ~49 auto-discovered from `fields_get()` (group "Others", see end of section).

| Field id (kept) | V1 type | R/W | V1 microdata | Template candidate(s) |
|---|---|---|---|---|
| `__shipping__name` | varchar | RO | organization/legalName | `Accounting.Supplier.SupplierName`, `Address.Contact.Name`, `ThirdParty.Core.Name` |
| `__shipping__contact` | varchar | RO | postaladdress/alternateName | `Address.Contact.AlternateName` |
| `__shipping__street` | varchar | RO | postaladdress/streetAddress | `Address.PostalAddress.StreetAddress` |
| `__shipping__zip` | varchar | RO | postaladdress/postalCode | `Address.PostalAddress.PostalCode` |
| `__shipping__city` | varchar | RO | postaladdress/addressLocality | `Address.PostalAddress.Locality` |
| `__shipping__state_name` | varchar | RO | / | **none** — keep custom |
| `__shipping__state_id` | state | RO | postaladdress/addressRegion | `Address.PostalAddress.RegionCode` |
| `__shipping__country_name` | varchar | RO | / | **none** — keep custom |
| `__shipping__country_code` | country | RO | postaladdress/addressCountry | `Address.PostalAddress.CountryCode` |
| `__shipping__phone` | varchar | RO | postaladdress/telephone | `ThirdParty.Core.Phone` |
| `__shipping__mobile` | varchar | RO | person/telephone | `Address.Contact.Phone`, `ThirdParty.Core.MobilePhone` |
| `amount_tax` | double | RO | product/Taxes | **none** — keep custom |
| `amount_total` | double | RO | product/Total | **none** — keep custom |
| `amount_untaxed` | double | RO | product/Untaxed Amount | **none** — keep custom |
| `client_order_ref` | varchar | W | order/orderNumber | `Order.Core.RefCustomer` |
| `create_date` | datetime | RO | datafeeditem/dateCreated | `Common.Audit.DateCreated` |
| `name` | varchar | RW | order/name | `Order.Core.RefInternal` |
| `write_date` | datetime | RO | datafeeditem/dateModified | `Common.Audit.DateModified` |
| `default_code@delivery` | varchar@list | W | orderitem/orderItemNumber | **none** — keep custom |
| `product_uom_qty@delivery` | int@list | RO | orderitem/orderQuantity | `Accounting.Receptions.Quantity` |
| `qty_delivered@delivery` | int@list | W | orderitem/orderItemStatus | `Accounting.Receptions.ReceivedQuantity` |
| `product_id@lines` | objectid::Product@list | W | product/productID | `Accounting.Items.ProductId` |
| `name@lines` | varchar@list | W | partofinvoice/description | `Accounting.Items.Description` |
| `product_uom_qty@lines` | int@list | W | quantitativevalue/value | `Accounting.Items.Quantity` |
| `qty_invoiced@lines` | int@list | RO | orderitem/orderQuantity | `Accounting.Receptions.Quantity` |
| `price_unit@lines` | price@list | W | pricespecification/price | `Accounting.Items.UnitPrice` |
| `discount@lines` | double@list | W | order/discount | `Accounting.Items.Discount` |
| `tax_name@lines` | varchar@list | RO | pricespecification/valueAddedTaxName | `Accounting.Items.VatCode` |
| `tax_names@lines` | inline@list | RO | pricespecification/valueAddedTaxNames | **none** — keep custom |
| `partner_id` | objectid::ThirdParty | RW | organization/ID | `Accounting.Core.ThirdParty`, `Address.Core.ThirdParty` |
| `partner_invoice_id` | objectid::Address | RW | order/billingAddress | `Accounting.Core.BillingAddress` |
| `partner_shipping_id` | objectid::Address | RW | order/orderDelivery | `Accounting.Core.ShippingAddress` |
| `date_order` | date | RW | order/orderDate | `Invoice.Core.Date`, `Order.Core.Date` |
| `user_id` | varchar | W | author/name | **none** — keep custom |
| `team_id` | varchar | W | author/memberOf | **none** — keep custom |
| `state` | varchar | W | order/orderStatus | `Order.Status.Status` |
| `isCanceled` | bool | RO | orderstatus/OrderCancelled | `Order.Status.IsCanceled` |
| `isValidated` | bool | RO | orderstatus/OrderPaymentDone | **none** — keep custom |
| `isProcessing` | bool | RO | orderstatus/OrderProcessing | `Order.Status.IsValidated` |
| `isClosed` | bool | RO | orderstatus/OrderDelivered | `Order.Status.IsClosed` |
| `safe_name` | — | — | not in old manifest | to check on 18.0 |
| `carrier_id` | — | — | not in old manifest | to check on 18.0 |
| `carrier_desc` | — | — | not in old manifest | to check on 18.0 |
| `qty_delivered@lines` | — | — | not in old manifest | to check on 18.0 |
| `qty_reserved@lines` | — | — | not in old manifest | to check on 18.0 |
| `company` | — | — | not in old manifest | to check on 18.0 |

Auto-discovered fields (49): `__last_update`, `access_token`, `access_url`, `access_warning`, `activity_date_deadline`, `activity_state`, `activity_summary`, `amount_by_group`, `amount_undiscounted`, `cart_quantity`, `cart_recovery_email_sent`, `commitment_date`, `confirmation_date`, `currency_rate`, `delivery_count`, `display_name`, `effective_date`, `expected_date`, `invoice_count`, `invoice_status`, `is_abandoned_cart`, `is_expired`, `lead_time@lines`, `message_attachment_count`, `message_has_error`, `message_has_error_counter`, `message_is_follower`, `message_needaction`, `message_needaction_counter`, `message_unread`, `message_unread_counter`, `note`, `only_services`, `origin`, `picking_policy`, `product_ref@lines`, `purchase_order_count`, `qty_delivered_manual@lines`, `reference`, `remaining_validity_days`, `require_payment`, `require_signature`, `signature`, `signed_by`, `state@lines`, `type_name`, `user_email`, `validity_date`, `warning_stock`

## Address

V1 manifest: 83 fields, of which ~65 auto-discovered from `fields_get()` (group "Others", see end of section).

| Field id (kept) | V1 type | R/W | V1 microdata | Template candidate(s) |
|---|---|---|---|---|
| `last` | varchar | W | person/givenName | `Address.Contact.Firstname`, `ThirdParty.Core.Lastname` |
| `first` | varchar | RW | person/familyName | `Address.Contact.Lastname`, `ThirdParty.Core.Firstname` |
| `active` | bool | W | person/active | **none** — keep custom |
| `create_date` | datetime | RO | datafeeditem/dateCreated | `Common.Audit.DateCreated` |
| `email` | email | W | contactpoint/email | `Address.Contact.Email`, `ThirdParty.Core.Email` |
| `function` | varchar | W | person/jobTitle | **none** — keep custom |
| `mobile` | phone | W | person/telephone | `Address.Contact.Phone`, `ThirdParty.Core.MobilePhone` |
| `phone` | phone | W | postaladdress/telephone | `ThirdParty.Core.Phone` |
| `type` | varchar | W | product/Address Type | **none** — keep custom |
| `website` | url | W | organization/url | `ThirdParty.Profile.Website` |
| `write_date` | datetime | RO | datafeeditem/dateModified | `Common.Audit.DateModified` |
| `street` | varchar | W | postaladdress/streetAddress | `Address.PostalAddress.StreetAddress` |
| `zip` | varchar | W | postaladdress/postalCode | `Address.PostalAddress.PostalCode` |
| `city` | varchar | W | postaladdress/addressLocality | `Address.PostalAddress.Locality` |
| `country_code` | country | W | postaladdress/addressCountry | `Address.PostalAddress.CountryCode` |
| `country_name` | varchar | W | postaladdress/addressCountryName | `Address.PostalAddress.CountryName` |
| `state_id` | state | W | postaladdress/addressRegion | `Address.PostalAddress.RegionCode` |
| `parent_id` | objectid::ThirdParty | RW | organization/ID | `Accounting.Core.ThirdParty`, `Address.Core.ThirdParty` |
| `company` | — | — | not in old manifest | to check on 18.0 |

Auto-discovered fields (65): `__last_update`, `activity_date_deadline`, `activity_state`, `activity_summary`, `additional_info`, `bank_account_count`, `barcode`, `color`, `comment`, `commercial_company_name`, `company_type`, `contact_address`, `contracts_count`, `credit`, `customer`, `date`, `debit`, `debit_limit`, `display_name`, `email_formatted`, `employee`, `has_unreconciled_entries`, `im_status`, `image`, `invoice_warn`, `invoice_warn_msg`, `is_blacklisted`, `is_company`, `journal_item_count`, `lang`, `last_time_entries_checked`, `message_attachment_count`, `message_bounce`, `message_has_error`, `message_has_error_counter`, `message_is_follower`, `message_needaction`, `message_needaction_counter`, `message_unread`, `message_unread_counter`, `name`, `parent_name`, `partner_gid`, `partner_share`, `payment_token_count`, `picking_warn`, `picking_warn_msg`, `purchase_order_count`, `purchase_warn`, `purchase_warn_msg`, `ref`, `sale_order_count`, `sale_warn`, `sale_warn_msg`, `signup_expiration`, `signup_token`, `signup_type`, `signup_url`, `signup_valid`, `supplier`, `supplier_invoice_count`, `total_invoiced`, `trust`, `tz`, `tz_offset`

## Product

V1 manifest: 121 fields, of which ~84 auto-discovered from `fields_get()` (group "Others", see end of section).

| Field id (kept) | V1 type | R/W | V1 microdata | Template candidate(s) |
|---|---|---|---|---|
| `code@attributes` | varchar@list | W | product/VariantAttributeName | `Product.Variants.AttributeName` |
| `name@attributes` | varchar@list | RO | / | **none** — keep custom |
| `value@attributes` | varchar@list | W | product/VariantAttributeValue | `Product.Variants.AttributeValue` |
| `price_extra@attributes` | double@list | W | product/VariantExtraPrice | **none** — keep custom |
| `active` | bool | W | product/active | `Product.Flags.Active` |
| `barcode` | varchar | W | product/Barcode | **none** — keep custom |
| `create_date` | datetime | RO | datafeeditem/dateCreated | `Common.Audit.DateCreated` |
| `default_code` | varchar | W | product/model | `Product.Core.ProductSku` |
| `description` | varchar | W | product/description | `Product.Core.ShortDescription` |
| `name` | varchar | RW | product/name | `Accounting.Items.ProductName`, `Product.Core.Name` |
| `purchase_ok` | bool | W | product/ordered | **none** — keep custom |
| `qty_available` | double | RO | product/Quantity On Hand | **none** — keep custom |
| `sale_ok` | bool | W | product/offered | `Product.Flags.Offered` |
| `type` | varchar | W | product/odooType | **none** — keep custom |
| `virtual_available` | double | RO | product/Forecast Quantity | **none** — keep custom |
| `volume` | double | W | product/Volume | `Product.Dimensions.Volume` |
| `website_url` | url | RO | product/urlRewrite | `Product.Seo.UrlRewrite` |
| `weight` | double | W | product/Weight | `Product.Dimensions.Weight` |
| `write_date` | datetime | RO | datafeeditem/dateModified | `Common.Audit.DateModified` |
| `image@Images` | image@list | W | product/image | `Product.Gallery.Image` |
| `position@Images` | int@list | W | product/positionImage | `Product.Gallery.Position` |
| `visible@Images` | bool@list | W | product/isVisibleImage | `Product.Gallery.IsVisible` |
| `cover@Images` | bool@list | W | product/isCover | `Product.Gallery.IsCover` |
| `list_price` | price | W | product/basePrice | `Product.Pricing.BasePrice` |
| `variant_price_extra` | price | RO | product/extraPrice | **none** — keep custom |
| `standard_price` | price | W | product/wholesalePrice | `Product.Pricing.WholesalePrice` |
| `categ_id` | varchar | RO | product/classificationId | **none** — keep custom |
| `categ` | varchar | W | product/classification | **none** — keep custom |
| `supplier_name` | varchar | W | product/supplierName | **none** — keep custom |
| `supplier_price_dbl` | double | W | product/supplierPriceDbl | **none** — keep custom |
| `supplier_price` | price | W | product/supplierPrice | **none** — keep custom |
| `supplier_sku` | varchar | W | product/mpn | `Accounting.Items.ProductMpn`, `Product.Identifiers.Mpn` |
| `supplier_min_qty` | int | W | product/supplierMinQty | **none** — keep custom |
| `supplier_currency` | currency | W | product/supplierCurrency | **none** — keep custom |
| `variant_template` | varchar | RO | product/isVariationOf | `Product.Variants.ParentProduct` |
| `id@variants` | objectid::Product@list | W | product/Variants | `Product.Variants.VariantList` |
| `sku@variants` | varchar@list | RO | / | **none** — keep custom |
| `tracking` | — | — | not in old manifest | to check on 18.0 |
| `is_storable` | — | — | not in old manifest | to check on 18.0 |
| `lst_price` | — | — | not in old manifest | to check on 18.0 |
| `variant_price` | — | — | not in old manifest | to check on 18.0 |
| `list_price_tax_ids` | — | — | not in old manifest | to check on 18.0 |
| `list_price_tax_names` | — | — | not in old manifest | to check on 18.0 |
| `standard_price_tax_names` | — | — | not in old manifest | to check on 18.0 |
| `product_brand` | — | — | not in old manifest | to check on 18.0 |
| `free_qty` | — | — | not in old manifest | to check on 18.0 |
| `company` | — | — | not in old manifest | to check on 18.0 |

Auto-discovered fields (84): `__last_update`, `accessory_products`, `activity_date_deadline`, `activity_state`, `activity_summary`, `alternative_products`, `available_threshold`, `cart_qty`, `code`, `color`, `custom_message`, `custom_message_fr_FR`, `description_fr_FR`, `description_picking`, `description_picking_fr_FR`, `description_pickingin`, `description_pickingin_fr_FR`, `description_pickingout`, `description_pickingout_fr_FR`, `description_purchase`, `description_purchase_fr_FR`, `description_sale`, `description_sale_fr_FR`, `display_name`, `expense_policy`, `hide_expense_policy`, `incoming_qty`, `inventory_availability`, `invoice_policy`, `is_product_variant`, `is_published`, `is_seo_optimized`, `message_attachment_count`, `message_has_error`, `message_has_error_counter`, `message_is_follower`, `message_needaction`, `message_needaction_counter`, `message_unread`, `name_fr_FR`, `nbr_reordering_rules`, `outgoing_qty`, `partner_ref`, `product_variant_count`, `property_cost_method`, `property_valuation`, `public_categ`, `public_categ_ids`, `purchase_line_warn_msg`, `purchase_method`, `purchased_product_qty`, `qty_at_date`, `rating_count`, `rating_last_value`, `rental`, `reordering_max_qty`, `reordering_min_qty`, `route_ids`, `routes`, `sale_delay`, `sale_line_warn_msg`, `sales_count`, `sequence`, `service_type`, `stock_value`, `uom_name`, `uom_name_fr_FR`, `value_fr_FR@attributes`, `website_meta_description`, `website_meta_description_fr_FR`, `website_meta_keywords`, `website_meta_keywords_fr_FR`, `website_meta_og_img`, `website_meta_title`, `website_meta_title_fr_FR`, `website_price`, `website_price_difference`, `website_public_price`, `website_published`, `website_sequence`, `website_size_x`, `website_size_y`, `weight_uom_name`, `weight_uom_name_fr_FR`

## Invoice

V1 manifest: 83 fields, of which ~44 auto-discovered from `fields_get()` (group "Others", see end of section).

| Field id (kept) | V1 type | R/W | V1 microdata | Template candidate(s) |
|---|---|---|---|---|
| `__shipping__name` | varchar | RO | organization/legalName | `Accounting.Supplier.SupplierName`, `Address.Contact.Name`, `ThirdParty.Core.Name` |
| `__shipping__contact` | varchar | RO | postaladdress/alternateName | `Address.Contact.AlternateName` |
| `__shipping__street` | varchar | RO | postaladdress/streetAddress | `Address.PostalAddress.StreetAddress` |
| `__shipping__zip` | varchar | RO | postaladdress/postalCode | `Address.PostalAddress.PostalCode` |
| `__shipping__city` | varchar | RO | postaladdress/addressLocality | `Address.PostalAddress.Locality` |
| `__shipping__state_name` | varchar | RO | / | **none** — keep custom |
| `__shipping__state_id` | state | RO | postaladdress/addressRegion | `Address.PostalAddress.RegionCode` |
| `__shipping__country_name` | varchar | RO | / | **none** — keep custom |
| `__shipping__country_code` | country | RO | postaladdress/addressCountry | `Address.PostalAddress.CountryCode` |
| `__shipping__phone` | varchar | RO | postaladdress/telephone | `ThirdParty.Core.Phone` |
| `__shipping__mobile` | varchar | RO | person/telephone | `Address.Contact.Phone`, `ThirdParty.Core.MobilePhone` |
| `amount_tax` | double | RO | product/Tax | **none** — keep custom |
| `amount_total` | double | RO | product/Total | **none** — keep custom |
| `amount_untaxed` | double | RO | product/Untaxed Amount | **none** — keep custom |
| `create_date` | datetime | RO | datafeeditem/dateCreated | `Common.Audit.DateCreated` |
| `date_due` | date | RO | invoice/paymentDueDate | `Invoice.Core.PaymentDueDate` |
| `name` | varchar | RO | product/Reference/Description | **none** — keep custom |
| `number` | varchar | W | invoice/confirmationNumber | `Invoice.Core.RefCustomer` |
| `write_date` | datetime | RO | product/Last Updated on | **none** — keep custom |
| `partner_id` | objectid::ThirdParty | RW | invoice/customer | **none** — keep custom |
| `partner_shipping_id` | objectid::Address | RW | order/orderDelivery | `Accounting.Core.ShippingAddress` |
| `date_invoice` | date | RW | order/orderDate | `Invoice.Core.Date`, `Order.Core.Date` |
| `product_id@lines` | objectid::Product@list | W | product/productID | `Accounting.Items.ProductId` |
| `name@lines` | varchar@list | W | partofinvoice/description | `Accounting.Items.Description` |
| `quantity@lines` | int@list | W | quantitativevalue/value | `Accounting.Items.Quantity` |
| `price_unit@lines` | price@list | W | pricespecification/price | `Accounting.Items.UnitPrice` |
| `discount@lines` | double@list | W | order/discount | `Accounting.Items.Discount` |
| `tax_name@lines` | varchar@list | RO | pricespecification/valueAddedTaxName | `Accounting.Items.VatCode` |
| `tax_names@lines` | inline@list | RO | pricespecification/valueAddedTaxNames | **none** — keep custom |
| `journal_code@payments` | varchar@list | W | invoice/PaymentMethod | `Accounting.Payments.PaymentMode` |
| `journal_name@payments` | varchar@list | RO | / | **none** — keep custom |
| `payment_date@payments` | date@list | W | paymentchargespecification/validFrom | `Accounting.Payments.PaymentDate` |
| `name@payments` | varchar@list | W | invoice/paymentMethodId | `Accounting.Misc.PaymentMethod`, `Accounting.Payments.PaymentNumber` |
| `amount@payments` | double@list | W | paymentchargespecification/price | `Accounting.Payments.PaymentAmount` |
| `state` | varchar | W | invoice/paymentStatus | `Invoice.Status.Status` |
| `isDraft` | bool | RO | paymentstatustype/InvoiceDraft | `Invoice.Status.IsDraft` |
| `isCanceled` | bool | RO | paymentstatustype/PaymentDeclined | `Invoice.Status.IsCanceled` |
| `isValidated` | bool | RO | paymentstatustype/PaymentDue | `Invoice.Status.IsValidated` |
| `isPaid` | bool | RO | paymentstatustype/PaymentComplete | `Invoice.Status.IsPaid` |
| `ref` | — | — | not in old manifest | to check on 18.0 |
| `invoice_date` | — | — | not in old manifest | to check on 18.0 |
| `date@payments` | — | — | not in old manifest | to check on 18.0 |
| `ref@payments` | — | — | not in old manifest | to check on 18.0 |
| `company` | — | — | not in old manifest | to check on 18.0 |

Auto-discovered fields (44): `__last_update`, `access_token`, `access_url`, `access_warning`, `activity_date_deadline`, `activity_state`, `amount_by_group`, `amount_tax_signed`, `amount_total_company_signed`, `amount_total_signed`, `amount_untaxed_invoice_signed`, `amount_untaxed_signed`, `comment`, `date`, `display_name`, `has_outstanding`, `invoice_icon`, `journal_type@payments`, `message_attachment_count`, `message_has_error`, `message_has_error_counter`, `message_is_follower`, `message_needaction`, `message_needaction_counter`, `origin`, `outstanding_credits_debits_widget`, `payment_type@payments`, `payments_widget`, `product_ref@lines`, `reconciled`, `reference`, `residual`, `residual_company_signed`, `residual_signed`, `sent`, `sequence_number_next`, `sequence_number_next_prefix`, `source_email`, `state@payments`, `team_id`, `type`, `user_email`, `user_id`, `vendor_display_name`

