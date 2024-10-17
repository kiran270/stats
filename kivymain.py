import requests
from bs4 import BeautifulSoup
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView

class StatsApp(App):
    def build(self):
        # Main layout for the app
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Input field for the Squad URL
        self.url_input = TextInput(hint_text='Enter squad URL', multiline=False, size_hint_y=None, height=50)
        layout.add_widget(self.url_input)

        # Dropdown-like selection for match type (using buttons for simplicity)
        self.type_label = Label(text='Select Match Type:', size_hint_y=None, height=40)
        layout.add_widget(self.type_label)
        
        # Button for T20 International (WT20)
        self.wt20_button = Button(text='WT20', size_hint_y=None, height=40)
        self.wt20_button.bind(on_press=self.set_wt20)
        layout.add_widget(self.wt20_button)

        # Button for Domestic T20 (MT20)
        self.mt20_button = Button(text='MT20', size_hint_y=None, height=40)
        self.mt20_button.bind(on_press=self.set_mt20)
        layout.add_widget(self.mt20_button)

        # Label to display selected match type
        self.selected_type = Label(text='Selected Match Type: None', size_hint_y=None, height=40)
        layout.add_widget(self.selected_type)

        # Submit button to fetch stats
        submit_btn = Button(text='Get Stats', size_hint_y=None, height=50)
        submit_btn.bind(on_press=self.get_stats)
        layout.add_widget(submit_btn)

        # Scrollable output for displaying the stats URLs
        self.scroll_view = ScrollView(size_hint=(1, 1))
        self.output_label = Label(text='', size_hint_y=None, height=500, markup=True)
        self.scroll_view.add_widget(self.output_label)
        layout.add_widget(self.scroll_view)

        return layout

    def set_wt20(self, instance):
        self.match_type = "23"
        self.selected_type.text = "Selected Match Type: WT20"

    def set_mt20(self, instance):
        self.match_type = "6"
        self.selected_type.text = "Selected Match Type: MT20"

    def get_stats(self, instance):
        squad_url = self.url_input.text
        ftype = self.match_type

        # Fetch and parse the squad page
        response = requests.get(squad_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        players = soup.find_all('a', class_='ds-inline-flex ds-items-start ds-leading-none')
        
        # Process players and generate URLs
        player_ids = []
        for x in players:
            temp = {}
            if x.has_attr('href'):
                if "cricketers" in x["href"]:
                    z = x["href"].split("/")
                    temp["name"] = z[2]
                    temp["role"] = "ALL"
                    if temp not in player_ids:
                        player_ids.append(temp)

        stats = []
        for i in player_ids:
            tempdata = {}
            tempsplit = i["name"].split("-")
            Batting_First = f"https://stats.espncricinfo.com/ci/engine/player/{tempsplit[-1]}.html?batting_fielding_first=1;class={ftype};filter=advanced;orderby=start;orderbyad=reverse;template=results;type=batting;view=innings"
            Bowling_First = f"https://stats.espncricinfo.com/ci/engine/player/{tempsplit[-1]}.html?batting_fielding_first=2;class={ftype};filter=advanced;orderby=start;orderbyad=reverse;template=results;type=bowling;view=innings"
            Batting_Second = f"https://stats.espncricinfo.com/ci/engine/player/{tempsplit[-1]}.html?batting_fielding_first=2;class={ftype};filter=advanced;orderby=start;orderbyad=reverse;template=results;type=batting;view=innings"
            Bowling_Second = f"https://stats.espncricinfo.com/ci/engine/player/{tempsplit[-1]}.html?batting_fielding_first=1;class={ftype};filter=advanced;orderby=start;orderbyad=reverse;template=results;type=bowling;view=innings"
            
            stat_entry = f"[b]{i['name']}[/b]\nBatting First: {Batting_First}\nBowling First: {Bowling_First}\nBatting Second: {Batting_Second}\nBowling Second: {Bowling_Second}\n"
            stats.append(stat_entry)

        # Display the stats in the output label
        self.output_label.text = "\n\n".join(stats)

if __name__ == '__main__':
    StatsApp().run()
