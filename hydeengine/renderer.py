import os
from django.conf import settings
from django.template.loader import render_to_string
from folders import ContentFolder
from sitemap import SitemapNode

def get_page_url(page):
    if settings.GENERATE_ABSOLUTE_FS_URLS:
        mirror = page.parent.get_mirror_folder(
                                settings.CONTENT_DIR, 
                                settings.DEPLOY_DIR, ignore_root=True)
        page_url = mirror.child(page.name)
    else:
        fragment = page.parent.get_fragment(settings.CONTENT_DIR)
        page_url = os.sep + fragment + page.name
    return page_url

def build_sitemap():
    class Builder(object):
        site = None
        current_node = None
        
        def visit_folder(self, folder):
            if not self.site:
                self.site = SitemapNode(None, folder, settings.SITE_NAME)
                self.current_node = self.site
                settings.CONTEXT['site'] = self.site
            else:
                parent = self.current_node.get_parent_of(folder)
                if parent:
                    self.current_node = parent.append_child(folder)
                    
        def visit_file(self, page):  
            self.current_node.add_page(page)
    builder = Builder()        
    ContentFolder().walk(builder, "[!_]*")
    builder.site.sort_and_link_pages()

def render_pages():
    for page in settings.CONTEXT['site'].walk_pages():
        settings.CONTEXT['page'] = page
        render_page(page)
            
def render_page(page):
    rendered = render_to_string(str(page), settings.CONTEXT)    
    page.write(rendered)