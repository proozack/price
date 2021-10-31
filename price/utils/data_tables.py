
class DataTablesUtils:
    def render(self, config):
        template = render_template( 
            'dt.html',
            resource = {
                'title': 'Tags by counting',
                'icon_path': ''.join([Config.STATIC_URL, '/logo.png']),
                'real_url': Config.REAL_URL,
                'static_url': Config.STATIC_URL,
                'description': 'Tags by counting',
                'year': now.year,
                'dt_table': [
                    'ID',
                    'Title',
                    'ID entry point',
                    'Name',
                    'Manufacturer',
                    'Cretaion date',
                ]
            },
            menu = ct.get_category_for_menu()
        )
        resp = make_response(template)
        resp.mimetype = 'text/html'
        return resp
