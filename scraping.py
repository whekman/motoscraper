
import re
from datetime import date, timedelta
from bs4 import BeautifulSoup as bs

class Listing:

    def __init__(self):
        
        self.title = None
        self.price = None
        self._date = None
        self._mileage = None

        self.scrape_date = date.today()
        
        self.im_src = None
        self.im_alt = None
        self.im_title = None

    @property
    def hash(self):

        if self.title is None:
            return -1

        if self.price is None:
            return -1
            
        else:        
            return hash(self.title + str(self.price)) % 100001
    
    @property
    def mileage(self):
        if self._mileage is None:
            return -1
        else:
            return int(re.findall(r'\d+\.\d+|\d+', self._mileage)[0].replace('.',''))

    @mileage.setter
    def mileage(self, mileage):
        self._mileage = mileage
    
    @property
    def price(self):
        if self._price is None:
            return - 1
        else:
            try:
                p = int(re.findall(r'\d+\.\d+|\d+', self._price)[0].replace('.',''))
                return p
            except:
                return - 1
        
    @price.setter
    def price(self, price):
        self._price = price
    
    @property
    def date(self):
        
        year_yy_most_recent = date.today().year - 2000 + 1
        
        month_abbrs = [x.strip() + '.' for x in "jan, feb, mrt, apr, mei, jun, jul, aug, sep, okt, nov, dec".split(",")]

        _d = self._date
        
        if "Vandaag" in _d:
            d = date.today()
        elif "Gisteren" in _d:
            d = date.today() - timedelta(days = 1)
        elif "Eergisteren" in _d:
            d = date.today() - timedelta(days = 2)
        else:
            # eg 20 feb. '24
            
            s = _d.replace("'","")
            day, month_abbr, year_abbr = s.split(" ")
            day = int(day)
        
            year_yy = int(year_abbr)
            
            if year_yy < year_yy_most_recent:
                year = year_yy + 2000
            else:
                year = year_yy + 1900
                
            month = month_abbrs.index(month_abbr) + 1
        
            d = date(year = year, month = month, day = day)
        
        return d

    @date.setter
    def date(self, date):
        self._date = date
    
    def _to_dict(self):
        return {x: self.__getattribute__(x) for x in dir(self) if not x.startswith('_')}

    def __repr__(self):

        lines = []
        
        attrs = [x for x in dir(self) if not x.startswith('_')]
        for attr in attrs:
            
            val = self.__getattribute__(attr)

            if val is None:
                continue
            
            if isinstance(val, int):
                lines.append("{:8.8}: {:20}...".format(attr, val))
            else:
                lines.append("{:8.8}: {:20.20}...".format(attr, val))

        return '\n'.join(lines)

def html_to_listings(html):
    
    soup = bs(html, "html.parser")
    
    ul = soup.find("ul", class_="hz-Listings hz-Listings--list-view")
    
    lis = ul.findAll("li")
    
    ims = []
    
    listings = []
    
    verbose = False
    
    for li in lis:
    
        l = Listing()
        
        p = li.prettify()
        
        if verbose: print(p,'\n')
        
        im = li.find("img")
    
        title = li.find("h3", class_ = "hz-Listing-title").text
        price = li.find("p", class_ = "hz-Listing-price hz-Listing-price--mobile hz-text-price-label").text
        text = li.find("p", class_ = "hz-Listing-description").text
        date = li.find("span", class_ ="hz-Listing-date hz-Listing-date--desktop").text
    
        mileage_div = li.find("div", class_ = "hz-Listing-attributes-nap-mileage")
        
        if mileage_div:
            mileage = mileage_div.find("span", class_="hz-Attribute hz-Attribute--default").text
            l.mileage = mileage

        trust_div = li.find("div", class_= "hz-Listing-trust-items-and-attributes")
        
        if trust_div:
            try:
                l.build_year = trust_div.find("span", class_="hz-Attribute hz-Attribute--default").text
            except:
                pass
            
        location_div = li.find("span", class_ = "hz-Listing-location")
        
        if location_div:
            location = location_div.find("span", class_ = "hz-Listing-distance-label").text
            l.location = location
            
        l.title = title
        l.price = price
        l.text = text
        l.date = date
        
        if im:
            try:
                l.im_src = im.attrs['src']
                l.im_alt = im.attrs['alt']
                l.im_title = im.attrs['title']
            except NameError as e:
                print("NameError:", e)
                pass
            except KeyError as e:
                print("KeyError:", e)
                pass
                
        listings.append(l)


    return listings