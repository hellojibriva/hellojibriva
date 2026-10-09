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
