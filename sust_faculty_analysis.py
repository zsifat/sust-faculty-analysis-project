from urllib.request import urlopen
from urllib.error import HTTPError, URLError
from bs4 import BeautifulSoup
import re
import matplotlib.pyplot as plt


def fetch_html(url):
    """
    Fetch HTML content from a URL and parse it with BeautifulSoup.
    """
    try:
        response = urlopen(url)
        return BeautifulSoup(response, 'lxml')
    except (HTTPError, URLError) as e:
        print(f"Error fetching URL: {e}")
        return None


def extract_faculty_names(bs):
    """
    Extract faculty names from the BeautifulSoup object.
    """
    if bs:
        faculty_names = bs.find('div', class_='department-faculty').find_all('h4')
        return [faculty.get_text().strip() for faculty in faculty_names]
    return []


def categorize_faculty(all_faculty):
    """
    Categorize faculty members into different ranks and statuses.
    """
    faculty_on_leave = []
    lecturer = []
    assistant_prof = []
    associate_prof = []
    professor = []
    head = []
    director = []

    for member in all_faculty:
        if '(On Leave)' in member or '(On Lien)' in member:
            faculty_on_leave.append(member)
        if 'Lecturer' in member:
            lecturer.append(member)
        if 'Assistant Professor' in member:
            assistant_prof.append(member)
        if 'Associate Professor' in member:
            associate_prof.append(member)
        if 'Professor' in member:
            professor.append(member)
        if 'Head' in member:
            head.append(member)
        if 'Director' in member:
            director.append(member)

    # Calculate number of professors excluding assistant and associate professors
    prof = len(professor) - (len(assistant_prof) + len(associate_prof))

    return {
        'On Leave': len(faculty_on_leave),
        'Lecturer': len(lecturer),
        'Assistant Professor': len(assistant_prof),
        'Associate Professor': len(associate_prof),
        'Professor': prof
    }


def plot_pie_chart(values, labels):
    """
    Plot a pie chart of faculty distribution.
    """
    colors = ['gold', 'lightcoral', 'lightskyblue', 'lightgreen']
    plt.figure(figsize=(16, 16))
    plt.pie(values, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
    plt.axis('equal')
    plt.title('Faculty Distribution by Rank')
    plt.show()


def plot_bar_chart(labels, values, title, xlabel, ylabel):
    """
    Plot a bar chart for faculty distribution or status.
    """
    colors = ['gold', 'lightcoral', 'lightskyblue', 'lightgreen']
    plt.figure(figsize=(10, 6))
    plt.bar(labels, values, color=colors)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.show()


def main():
    # Fetch and process data
    deptlinks = []
    bs = fetch_html('https://www.sust.edu/academics/schools')
    if bs:
        dept_links = bs.find_all('a', href=re.compile(r'https://www.sust.edu/d/\w{3}$'))
        for dept in dept_links:
            link = dept['href']
            deptlinks.append(link)
        deptlinks.append('https://www.sust.edu/institutes/iict/faculty')

        faculty_links = [links + '/faculty' for links in deptlinks]
        all_faculty = []
        for url in faculty_links:
            bs = fetch_html(url)
            faculty_names = extract_faculty_names(bs)
            all_faculty.extend(faculty_names)

        # Categorize and analyze data
        categorized_data = categorize_faculty(all_faculty)
        print('On leave:', categorized_data['On Leave'])
        print('Lecturer:', categorized_data['Lecturer'])
        print('Assistant Professor:', categorized_data['Assistant Professor'])
        print('Associate Professor:', categorized_data['Associate Professor'])
        print('Professor:', categorized_data['Professor'])

        # Data for charts excluding 'On Leave'
        labels = ['Lecturer', 'Assistant Professor', 'Associate Professor', 'Professor']
        values = [categorized_data['Lecturer'], categorized_data['Assistant Professor'],
                  categorized_data['Associate Professor'], categorized_data['Professor']]

        # Plotting
        plot_pie_chart(values, labels)

        # Plot bar charts
        plot_bar_chart(labels, values, 'Faculty Distribution by Rank', 'Faculty Rank', 'Number of Faculty')

        # Bar chart for On leave vs present
        leave_vs_present = [categorized_data['On Leave'], len(all_faculty) - categorized_data['On Leave']]
        plot_bar_chart(['On Leave', 'Present'], leave_vs_present, 'Leave vs Present', 'Status', 'Number of Faculty')


if __name__ == "__main__":
    main()
