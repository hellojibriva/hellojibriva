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
