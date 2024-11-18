import requests
from bs4 import BeautifulSoup

# Base URL for the main athletes page
base_url = 'https://www.onefc.com/athletes/page/'  # Adjust the URL based on the pagination pattern
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

page_number = 1  # Start from the first page
processed_urls = set()  # Set to keep track of processed fighter URLs

# Loop through the pages until no more athlete links are found
while True:
    # Construct the URL for the current page
    url = f"{base_url}{page_number}/"
    print(f"Scraping athletes page: {url}")

    # Send GET request
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"Failed to retrieve page {page_number}. Status code: {response.status_code}")
        break

    # Parse the page content
    main_page_soup = BeautifulSoup(response.content, 'html.parser')

    # Find all links to individual athlete pages
    athlete_links = main_page_soup.find_all('a', href=True)

    # Filter links that contain '/athletes/' in the URL
    fighter_urls = list(set(link['href'] for link in athlete_links if '/athletes/' in link['href']))

    # If no athlete links are found, stop the loop
    if not fighter_urls:
        print("No more athlete links found. Stopping the scraping process.")
        break

    print(f"Found {len(fighter_urls)} unique athlete links on page {page_number}.")

    # Scrape each individual fighter's page
    for fighter_url in fighter_urls:
        # Skip if this URL has already been processed
        if fighter_url in processed_urls:
            continue

        print(f"Scraping {fighter_url}...")
        fighter_response = requests.get(fighter_url, headers=headers)

        if fighter_response.status_code == 200:
            fighter_soup = BeautifulSoup(fighter_response.content, 'html.parser')

            # Mark the URL as processed
            processed_urls.add(fighter_url)

            # Scrape the fighter's name
            name_tag = fighter_soup.find('h1', class_='use-letter-spacing-hint')
            if name_tag:
                name = name_tag.text.strip()
                print(f"Fighter Name: {name}")
            else:
                print(f"Fighter name not found for {fighter_url}")

            # Scrape the fighter's weight
            weight = fighter_soup.find('h5', string='Weight Limit')
            if weight:
                rw = weight.find_next('div', class_='value').text.strip()
                print(f"Fighter Weight: {rw}")
            else:
                print(f"Fighter weight not found for {fighter_url}")

            # Scrape the fighter's titles
            titles = [div.get_text(separator=' ').strip() for div in fighter_soup.find_all('h4', class_='athlete-title')]

            if titles:
                for title in titles:
                    print(f"Fighter Title: {title}")
            else:
                print(f"Fighter title not found for {fighter_url}")

        else:
            print(f"Failed to retrieve {fighter_url}")

    # Move to the next page
    page_number += 1

print("Scraping completed.")
