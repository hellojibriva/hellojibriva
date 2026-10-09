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
