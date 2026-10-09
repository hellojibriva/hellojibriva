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
