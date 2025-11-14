from base_operates import click_element_by_ele


def if_not_selected_click(page, ele):
    if ele.attr('class') != 'chat-label-item selected':
        click_element_by_ele(page, ele)
