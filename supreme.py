from selenium import webdriver
from selenium.webdriver.support.ui import Select
from requests_html import HTMLSession, AsyncHTMLSession
import time
import re
import config

'''
python supreme.py --name="North Face"
'''

base_url = 'https://www.supremenewyork.com'


def get_product_links():
    '''
    Returns list of elements "items",
    each containing a link to product detail page
    '''
    base_shop = base_url + '/shop'
    session = HTMLSession()
    r = session.get(base_shop)
    items = r.html.find('#shop-scroller', first=True).find('li')
    return items, session


def get_matched_and_available(target_name):
    '''
    Given a target name, filter the product on main page,
    and return links to products with available items

    checked_urls: if already checked (and not a match in product name),
    skip in future checks

    Exactly how this should work, depends on how the drop works - is the page already there,
    just not for sale yet? Or page is added at drop time?
    '''
    target_name_list = [x.lower() for x in target_name.split(' ')]
    potential_urls = []
    items, session = get_product_links()
    for item in items:
        target_url = base_url + item.find('a', first=True).attrs['href']
        r = session.get(target_url)
        product_name = r.html.find('h1[itemprop=name]', first=True).text.lower()

        found = True
        for q in target_name_list:
            if q not in product_name:
                found = False
                break
        print('**************************')
        if found:
            print(f'Found a match: {product_name}')
            # check if can buy
            if check_can_buy(r):
                print('Still available.')
                potential_urls.append(target_url)
            else:
                print('No longer available')

        else:
            print(f'Not a match: {product_name}')

    return potential_urls


def check_can_buy(r):
    '''
    Given a page (returned by session.get(target_url)),
    find if there is such html code within:
    <input type="submit" name="commit" value="add to cart" class="button">
    Returns True if so, False if not
    '''
    buy_btn = r.html.find('input[value="add to basket"]', first=True)
    return (buy_btn is not None)



def perform_purchase(url):
    '''
    Given url of product, add to cart then checkout
    '''
    driver = webdriver.Safari()
    # url = "https://www.supremenewyork.com/shop/shirts/p4skltm3i" #a redirect to a login page occurs
    driver.get(url)
    btn = driver.find_element_by_id('add-remove-buttons').find_elements_by_tag_name('input')
    if len(btn) == 0:
        print('not available, DONE')
        return

    btn[0].click()
    time.sleep(1)

    # go to checkout
    checkout_url = 'https://www.supremenewyork.com/checkout'
    driver.get(checkout_url)
    # fill in form
    driver.find_element_by_id('order_billing_name').send_keys(config.NAME)
    driver.find_element_by_id('order_email').send_keys(config.EMAIL)
    driver.find_element_by_id('order_tel').send_keys(config.PHONE)
    driver.find_element_by_id('order_billing_address').send_keys(config.ADDRESS)
    driver.find_element_by_id('order_billing_zip').send_keys(config.ZIPCODE)
    driver.find_element_by_id('order_billing_city').send_keys(config.CITY)
    driver.find_element_by_id('credit_card_number').send_keys(config.CREDIT_CARD)
    driver.find_element_by_id('credit_card_verification_value').send_keys(config.CC_CVV)
    # driver.find_element_by_id('order_terms').click()
    # driver.find_element_by_id('store_address').click()

    # remove overlay
    ins_tags = driver.find_elements_by_tag_name('ins')
    for el in ins_tags:
        el.click()

    # selections
    # driver.find_element_by_id('order_billing_state').send_keys(config.STATE)
    # driver.find_element_by_id('credit_card_month').send_keys(config.CC_MONTH)
    # driver.find_element_by_id('credit_card_year').send_keys(config.CC_YEAR)

    #select = Select(driver.find_element_by_id('order_billing_state'))
    #select.select_by_value(config.STATE)
    select = Select(driver.find_element_by_id('credit_card_month'))
    select.select_by_value(config.CC_MONTH)
    select = Select(driver.find_element_by_id('credit_card_year'))
    select.select_by_value(config.CC_YEAR)

    time.sleep(2)

    # pay
    pay_btn = driver.find_element_by_id('pay').find_elements_by_tag_name('input')
    #pay_btn[0].click()


def main(target_product):
    urls = get_matched_and_available(target_product)
    print(f'Found {len(urls)} matches.')
    if len(urls) == 0:
        print('No match found - checking again')
        return
    print(f'Processing first url: {urls[0]}')
    # just buy the first match
    url = urls[0]
    perform_purchase(url)
    print('Done.')


#define main
if __name__ == '__main__':
    main('700-Fill Down')

    '''
    import argparse
    parser = argparse.ArgumentParser(description='Supremebot main parser')
    parser.add_argument('--name', required=True,
                        help='Specify product name to find and purchase')
    args = parser.parse_args()
    main(target_product=args.name)
    '''




