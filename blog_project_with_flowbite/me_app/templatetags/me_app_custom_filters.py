from django import template

register = template.Library()

@register.simple_tag
def get_proper_elided_page_range(paginator, number, on_each_side=2, on_ends=1):
    """
    Return a list of page numbers with proper elision:
    - Always show first and last pages
    - Show 'on_each_side' pages before and after current page
    - Show 'on_ends' pages from each end
    - Use ellipsis for gaps
    """
    page_range = list(paginator.page_range)
    total_pages = len(page_range)
    current_page = number

    # If the page range is smaller than 2*(on_each_side+on_ends+1), display all pages
    if total_pages <= (on_each_side + on_ends) * 2 + 1:
        return page_range

    # Determine left and right ranges
    left = max(1, current_page - on_each_side)
    right = min(total_pages, current_page + on_each_side)

    # Build the list of ranges and ellipsis positions
    page_list = []
    
    # Handle left side
    if left > 2:
        page_list.extend(range(1, on_ends + 1))
        page_list.append('...')
        page_list.extend(range(left, current_page))
    else:
        page_list.extend(range(1, current_page))

    # Add current page
    page_list.append(current_page)

    # Handle right side
    if right < total_pages - 1:
        page_list.extend(range(current_page + 1, right + 1))
        page_list.append('...')
        page_list.extend(range(total_pages - on_ends + 1, total_pages + 1))
    else:
        page_list.extend(range(current_page + 1, total_pages + 1))

    return page_list