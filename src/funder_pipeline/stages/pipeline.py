from funder_pipeline.stages.extract.fetch_openAlex import export_awards_per_funder
from funder_pipeline.stages.extract.remove_invalid import filter_invalid_assets
from funder_pipeline.stages.transform.routing import route_all_awards_to_handlers


def get_award_data(startYear, endYear, openAlex_id, institutionsId="I6902469"):

    # 1. fetch assets info and associated award data from OpenAlex
    # a copy of data is stored
    funder_name, output_dir, assets_awards = export_awards_per_funder(
        funder_id=openAlex_id,
        institution_id=institutionsId,
        start_year=startYear,
        end_year=endYear
    )

    print(f"Assets and Awards info for {funder_name} exported to {output_dir}")
    print(f"Total awards for {funder_name}: {len(assets_awards)}")
    print()

    # 2. Call the Espero API to filter out the assets that is not associated with a faculty (sometimes, it contains assets from a students)
    valid_awards, invalid_dois, invalid_asset_output_dir = filter_invalid_assets(assets_awards, funder_name, startYear, endYear)
    print(f"Valid awards for {funder_name}: {len(valid_awards)}")
    print(f"Invalid awards for {funder_name}: {len(invalid_dois)}; their doi are in {invalid_asset_output_dir}")
    print()

    # 3. Route the awards to different handlers based on the funder id or award ID patterns
    routing_outcomes, routing_outcomes_output_dir = route_all_awards_to_handlers(valid_awards, openAlex_id, funder_name, startYear, endYear)
    print(f"Routing outcomes for {funder_name} saved to {routing_outcomes_output_dir}")
    print()

    






