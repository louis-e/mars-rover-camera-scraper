import requests, os

api_key = 'API_KEY'
api_url = 'https://api.nasa.gov/mars-photos/api/v1/rovers/'

def get_rover_data():
    r = requests.get(api_url + '?api_key=' + api_key)
    data = r.json()
    return data

def get_photos(rover, sol, camera):
    sol_pic = False
    retry_count = 0
    while not sol_pic:
        r = requests.get(api_url + rover + '/photos?sol=' + str(sol) + '&camera=' + camera + '&api_key=' + api_key)
        if r.status_code != 200:
            print(f"Error {r.status_code} while fetching photos for rover {rover} on Sol {sol} with camera {camera}")
            return []
        data = r.json()
        
        if data['photos'] or retry_count > 2:
            sol_pic = True
        else:
            sol -= 1
            retry_count += 1
    return data['photos']

def download_photos(camera_data, camera_name, path):
    img_data = requests.get(camera_data[len(camera_data) - 1]['img_src']).content
    with open(path + camera_name + '.jpg', 'wb') as handler:
        handler.write(img_data)

def main():
    rover_data = get_rover_data()
    path = 'frontend/images/'
    if not os.path.exists(path):
        os.makedirs(path)
    
    for rover in rover_data['rovers']:
        path = 'frontend/images/' + rover['name'] + '/'
        if not os.path.exists(path):
            os.makedirs(path)

        if (rover['status'] == 'complete'):
            print(f"Skipping rover {rover['name']} (rover status: {rover['status']})")
            continue
        print(f"Scraping rover {rover['name']}, starting with Sol {rover['max_sol']} (rover status: {rover['status']})")
        for camera in rover['cameras']:
            print(f"Scraping camera {rover['name']}@{camera['name']} ({camera['full_name']})")
            camera_data = get_photos(rover['name'], rover['max_sol'], camera['name'])
            if not camera_data:
                continue
            download_photos(camera_data, camera['name'], path)

if __name__ == '__main__':
    main()