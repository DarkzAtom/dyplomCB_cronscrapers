import all_links_collector
import async_individual_link_processor
import csv
import asyncio


async def main():
    collected_links_list = all_links_collector.get_all_links_of_articles_until_lastsaved_met()
    final_list = await async_individual_link_processor.process_links_async(collected_links_list)
    
    # saving into the csv for now since we don't have a database yet
    # TODO: save into the database as a superstructure to the existing logic with saving to the csv

    csv_file = "output.csv"

    if final_list:
        with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=final_list[0].keys())
            writer.writeheader()
            for data in final_list:
                writer.writerow(data)
    else:
        print("No data to save")


if __name__ == "__main__":
    asyncio.run(main())

