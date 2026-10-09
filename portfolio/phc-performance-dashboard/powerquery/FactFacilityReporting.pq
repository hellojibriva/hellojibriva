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
