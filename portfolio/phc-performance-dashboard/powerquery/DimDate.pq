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
