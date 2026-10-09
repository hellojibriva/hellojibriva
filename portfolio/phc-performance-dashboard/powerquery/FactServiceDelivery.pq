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
