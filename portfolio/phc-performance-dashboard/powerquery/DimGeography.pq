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
