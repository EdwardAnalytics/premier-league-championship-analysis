# # Check for dupes
# # Step 3: Check for duplicates in the result DataFrame
# duplicates_result = (
#     pl_champ_merged.groupby(["Player", "Country", "season_start_premier_league"])
#     .size()
#     .reset_index(name="count")
# )

# # Filter for duplicates (count > 1)
# duplicates_result = duplicates_result[duplicates_result["count"] > 1]

# # Test - check promoted teams correct
# # Grouping by 'Team (Champ)' and 'Season (Champ)', counting occurrences
# grouped_df = (
#     pl_champ_merged[pl_champ_merged["With Promoted Team"] == 1]
#     .groupby(["Season Start (Champ.)", "Team (Champ.)"])
#     .size()
#     .reset_index(name="Count")
# )

# # Sorting by 'Team (Champ)' and 'Season (Champ)'
# sorted_grouped_df = grouped_df.sort_values(
#     by=["Season Start (Champ.)", "Team (Champ.)"]
# )
# sorted_grouped_df.head(10)
