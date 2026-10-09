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
