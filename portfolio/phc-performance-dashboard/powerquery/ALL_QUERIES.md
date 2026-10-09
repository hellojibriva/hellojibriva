# Power Query (M) scripts

Create the `DataFolder` parameter first, then for each table: *Home › New source › Blank query › Advanced editor*, paste the script and rename the query to the file name (without `.pq`). All queries read only the anonymized CSVs in `../data`. `DataFolder` is a parameter and is not loaded as a table.

## FactServiceDelivery

```powerquery
// FactServiceDelivery – loads data/fact_service_delivery.csv
let
    Source = Csv.Document(File.Contents(DataFolder & "fact_service_delivery.csv"), [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    Typed = Table.TransformColumnTypes(Promoted, {
        {"FacilityKey", Int64.Type},
        {"MonthDate", type date},
        {"IndicatorKey", Int64.Type},
        {"Value", Int64.Type},
        {"ValueStatus", type text}
    })
in
    Typed
```

## FactFacilityReporting

```powerquery
// FactFacilityReporting – loads data/fact_facility_reporting.csv
let
    Source = Csv.Document(File.Contents(DataFolder & "fact_facility_reporting.csv"), [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    Typed = Table.TransformColumnTypes(Promoted, {
        {"FacilityKey", Int64.Type},
        {"MonthDate", type date},
        {"Expected", Int64.Type},
        {"Reported", Int64.Type},
        {"ReportingStatus", type text}
    })
in
    Typed
```

## FactMortality

```powerquery
// FactMortality – loads data/fact_mortality_national_month.csv
let
    Source = Csv.Document(File.Contents(DataFolder & "fact_mortality_national_month.csv"), [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    Typed = Table.TransformColumnTypes(Promoted, {
        {"MonthDate", type date},
        {"IndicatorKey", Int64.Type},
        {"Deaths", Int64.Type}
    })
in
    Typed
```

## FactDataQuality

```powerquery
// FactDataQuality – loads data/fact_data_quality.csv
let
    Source = Csv.Document(File.Contents(DataFolder & "fact_data_quality.csv"), [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    Typed = Table.TransformColumnTypes(Promoted, {
        {"FacilityKey", Int64.Type},
        {"MonthDate", type date},
        {"CheckCode", type text},
        {"Check", type text},
        {"CheckType", type text}
    })
in
    Typed
```

## DimFacility

```powerquery
// DimFacility – loads data/dim_facility.csv
let
    Source = Csv.Document(File.Contents(DataFolder & "dim_facility.csv"), [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    Typed = Table.TransformColumnTypes(Promoted, {
        {"FacilityKey", Int64.Type},
        {"Facility", type text},
        {"AdopterKey", Int64.Type},
        {"ZoneKey", Int64.Type}
    })
in
    Typed
```

## DimAdopter

```powerquery
// DimAdopter – loads data/dim_adopter.csv
let
    Source = Csv.Document(File.Contents(DataFolder & "dim_adopter.csv"), [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    Typed = Table.TransformColumnTypes(Promoted, {
        {"AdopterKey", Int64.Type},
        {"Adopter", type text},
        {"FacilitiesInProgramme", Int64.Type}
    })
in
    Typed
```

## DimGeography

```powerquery
// DimGeography – loads data/dim_geography.csv
let
    Source = Csv.Document(File.Contents(DataFolder & "dim_geography.csv"), [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    Typed = Table.TransformColumnTypes(Promoted, {
        {"ZoneKey", Int64.Type},
        {"Zone", type text},
        {"ZoneSort", Int64.Type},
        {"IsSuppressedGroup", Int64.Type}
    })
in
    Typed
```

## DimIndicator

```powerquery
// DimIndicator – loads data/dim_indicator.csv
let
    Source = Csv.Document(File.Contents(DataFolder & "dim_indicator.csv"), [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    Typed = Table.TransformColumnTypes(Promoted, {
        {"IndicatorKey", Int64.Type},
        {"IndicatorCode", type text},
        {"Indicator", type text},
        {"ServiceCategory", type text},
        {"Unit", type text},
        {"SortOrder", Int64.Type},
        {"Additive", Int64.Type},
        {"FirstMonthCaptured", type date}
    })
in
    Typed
```

## DimDate

```powerquery
// DimDate – contiguous daily calendar for 2026 (required for DATEADD time intelligence). Mark as date table on [Date].
// Facts are stored at month grain and join on the first day of the month.
let
    StartDate = #date(2026, 1, 1),
    EndDate = #date(2026, 12, 31),
    Dates = List.Dates(StartDate, Duration.Days(EndDate - StartDate) + 1, #duration(1, 0, 0, 0)),
    Base = Table.FromList(Dates, Splitter.SplitByNothing(), {"Date"}),
    Typed = Table.TransformColumnTypes(Base, {{"Date", type date}}),
    AddYear = Table.AddColumn(Typed, "Year", each Date.Year([Date]), Int64.Type),
    AddQ = Table.AddColumn(AddYear, "Quarter", each "Q" & Text.From(Date.QuarterOfYear([Date])), type text),
    AddQL = Table.AddColumn(AddQ, "Quarter Label", each [Quarter] & " " & Text.From([Year]), type text),
    AddMN = Table.AddColumn(AddQL, "Month Number", each Date.Month([Date]), Int64.Type),
    AddMName = Table.AddColumn(AddMN, "Month Name", each Date.ToText([Date], "MMMM", "en-GB"), type text),
    AddMShort = Table.AddColumn(AddMName, "Month Short", each Date.ToText([Date], "MMM", "en-GB"), type text),
    AddMStart = Table.AddColumn(AddMShort, "Month Start", each Date.StartOfMonth([Date]), type date),
    AddYM = Table.AddColumn(AddMStart, "Year Month", each Date.ToText([Date], "yyyy-MM"), type text),
    AddProg = Table.AddColumn(AddYM, "Is Programme Month", each if [Date] <= #date(2026, 9, 30) then 1 else 0, Int64.Type)
in
    AddProg
```

## DataFolder (parameter)

```powerquery
// Create via Home > Manage Parameters > New parameter:
//   Name: DataFolder   Type: Text   Current value: full path of the portfolio "data" folder, ending with a backslash,
//   e.g. C:\Portfolio\phc-performance-dashboard\data\
// Equivalent M (Advanced Editor of a blank query named DataFolder):
"C:\Portfolio\phc-performance-dashboard\data\" meta [IsParameterQuery = true, Type = "Text", IsParameterQueryRequired = true]
```

