import flet as ft
from read import file_reading, file_print

settings = file_reading('settings.json')
file = settings['data_file']



class Main():
    def __init__(self) -> None:
        self.__login = self.__Login()
        self.__table = self.__DataTable()
        self.__app_bar = self.__AppBar()
        self.__end_drawer = self.__EndDrawer(self.__all_filters)

    def __add_dialog(self, page: ft.Page):
        add = [
            ft.TextField(label='Название'),
            ft.TextField(label='Производитель'),
            ft.TextField(label='Цена', input_filter=ft.NumbersOnlyInputFilter()),
            ft.TextField(label='Срок годности'),
            ft.TextField(label='Количество на складе',
                         input_filter=ft.NumbersOnlyInputFilter())
        ]

        def add_info(e):
            info = [i.value for i in add]
            print(info)
            if all(info):
                data = file_reading(file)
                data = list(data)
                data.append({
                    "Название": info[0],
                    "Производитель": info[1],
                    "Цена": int(info[2]),
                    "Срок годности": info[3],
                    "Количество на складе": int(info[4])
                })
                file_print(file, data)
                self.__table.fill_update(page)
                page.close_dialog()
            else:
                page.snack_bar = ft.SnackBar(ft.Text(
                    'Замечено пустое поле', color='red', text_align=ft.TextAlign.CENTER), True)
            page.update()

        page.dialog = ft.AlertDialog(True, ft.Text('Добавление'),
                                     ft.Column(add, height=350), [
            ft.TextButton(text='Добавить', icon=ft.icons.ADD,
                          on_click=add_info),
            ft.TextButton(text='Отмена', icon=ft.icons.CANCEL,
                          on_click=lambda e: page.close_dialog())
        ], open=True)
        page.update()

    def __show_menu(self, page: ft.Page):
        page.end_drawer.open =True
        page.update()

    def __all_filters(self, page: ft.Page):
        self.__table.fill_update(page)
        if all([self.__app_bar.search_text.value]):
            self.__table.search(page, self.__app_bar.search_text.value, 'Название')
        info = [i.value for i in self.__end_drawer.filters]
        if all([info[0]]):
            self.__table.search(page, info[0], 'Department')
        if all([info[1]]):
            self.__table.search(page, info[1], 'Job_title')
        if all([info[2], info[3]]):
            self.__table.search_int(
                page,
                int(info[2]),
                int(info[3]),
                'Age')
        if all([info[4], info[5]]):
            self.__table.search_int(
                page,
                int(info[4]),
                int(info[5]),
                'Wage')

    def render(self, page: ft.Page):
        page.scroll = True
        page.window_min_width = 1000
        page.window_min_height = 500
        page.theme_mode = settings['theme']
        page.adaptive = True

        page.overlay.append(self.__app_bar.file_dir)

        self.__app_bar.update.on_click = lambda e: self.__default(page)
        self.__app_bar.add.on_click = lambda e: self.__add_dialog(page)
        self.__app_bar.themes.on_click = lambda e: self.__themes(page)
        # self.__app_bar.more.on_click = 
        self.__app_bar.search_text.on_change = lambda e: self.__all_filters(
            page)

        self.__app_bar.file_dir.on_result = lambda e: self.__table.save(e.path)

        def panel_info():
            page.add(ft.Column([self.__table.render(page)],
                     horizontal_alignment=ft.CrossAxisAlignment.STRETCH))
            page.appbar = self.__app_bar.appbar
            page.end_drawer = self.__end_drawer.draver
            self.__default(page)

        page.snack_bar = ft.SnackBar(ft.Text(
            'Неверные данные входа', color='red', text_align=ft.TextAlign.CENTER), bgcolor='white')
        self.__login.render(page, panel_info)

        page.window_center()

    class __Login():
        def __init__(self) -> None:
            self.__user_login = ft.TextField(label='Логин', width=240)
            self.__user_pass = ft.TextField(
                label='Пароль', width=240, password=True, can_reveal_password=True)
            self.__btn_verif = ft.TextButton('Вход', width=100, disabled=True)

        def render(self, page: ft.Page, open):
            def validate(e) -> None:
                if all([self.__user_login.value, self.__user_pass.value.strip()]):
                    self.__btn_verif.disabled = False
                else:
                    self.__btn_verif.disabled = True
                self.__btn_verif.update()

            self.__user_login.on_change = validate
            self.__user_pass.on_change = validate

            def verication(e):
                if self.__user_login.value.strip() == 'admin' and self.__user_pass.value.strip() == 'admin':
                    open()
                    page.close_dialog()
                else:
                    page.snack_bar = ft.SnackBar(ft.Text(
                        'Неверные данные входа', color='red', text_align=ft.TextAlign.CENTER), bgcolor='white', open=True)
                page.update()

            self.__user_pass.on_submit = verication
            self.__btn_verif.on_click = verication

            page.dialog = ft.AlertDialog(True, ft.Text('Авторизация'),
                                         ft.Column([self.__user_login, self.__user_pass], height=150,
                                                   alignment=ft.MainAxisAlignment.CENTER), [self.__btn_verif],
                                         actions_alignment=ft.MainAxisAlignment.CENTER, open=True)
            page.update()

            self.__user_login.on_submit = lambda e: self.__user_pass.focus()
            self.__user_login.focus()

    class __DataTable():
        def __init__(self) -> None:
            self.ref = ft.Ref[ft.DataTable]()
            self.__data = [self.__DataRow(i, obj)
                           for i, obj in enumerate(file_reading(file))]

        class __Employee():
            def __init__(self, obj: object) -> None:
                self._Department = obj['Department']
                self._Name = obj['Name']
                self._Job_title = obj['Job_title']
                self._Age = obj['Age']
                self._Wage = obj['Wage']

            def show(self):
                return {
                    'Department': self._Department,
                    'Name': self._Name,
                    'Job_title': self._Job_title,
                    'Age': self._Age,
                    'Wage': self._Wage
                }

            def show_text(self):
                data = str(self._Department).ljust(40) + str(self._Name).ljust(15) + str(
                    self._Job_title).ljust(40) + str(self._Age).rjust(5) + str(self._Wage).rjust(8)
                return data

        class __DataRow(__Employee):
            def __init__(self, id: int, obj: object) -> None:
                super().__init__(obj)
                self.__id = id
                self.__edit = [
                    ft.TextField(label='Отдел'),
                    ft.TextField(label='ФИО'),
                    ft.TextField(label='Должность'),
                    ft.TextField(label='Возраст', input_filter=ft.NumbersOnlyInputFilter()),
                    ft.TextField(label='Заработная плата', input_filter=ft.NumbersOnlyInputFilter())
                ]
                self.Row = ft.Ref[ft.DataRow]()

            def __open_edit(self, page: ft.Page):
                self.__edit[0].value = self._Department
                self.__edit[1].value = self._Name
                self.__edit[2].value = self._Job_title
                self.__edit[3].value = self._Age
                self.__edit[4].value = self._Wage
                 
                def save_info(e):
                    info = [i.value for i in self.__edit]
                    if all(info):
                        data = file_reading(file)
                        data[self.__id] = {
                            'Department': info[0],
                            'Name': info[1],
                            'Job_title': info[2],
                            'Age': int(info[3]),
                            'Wage': int(info[4])
                        }
                        file_print(file, data)
                        self._Department = info[0]
                        self._Name = info[1]
                        self._Job_title = info[2]
                        self._Age = int(info[3])
                        self._Wage = int(info[4])
                        for i in range(5):
                            self.Row.current.cells[i].content.value = info[i]
                        self.Row.current.data = data[self.__id]
                        self.Row.current.update()
                        page.close_dialog()
                    else:
                        page.snack_bar = ft.SnackBar(ft.Text(
                            'Замечено пустое поле', color='red', text_align=ft.TextAlign.CENTER), True)

                page.dialog = ft.AlertDialog(True, ft.Text('Редактирование'),
                                             ft.Column(
                                                 self.__edit, height=350),
                                             actions=[
                    ft.TextButton(text='Сохранить',
                                  icon=ft.icons.SAVE, on_click=save_info),
                    ft.TextButton(text='Отмена', icon=ft.icons.CANCEL,
                                  on_click=lambda e: page.close_dialog()),
                    ft.TextButton(text='Удалить', icon=ft.icons.DELETE, on_click=lambda e: self.__open_delete(
                        page), icon_color='red', style=ft.ButtonStyle('red'))
                ],
                    open=True
                )
                page.update()

            def __open_delete(self, page: ft.Page):
                def delete_info(e):
                    data = file_reading(file)
                    data.pop(self.__id)
                    file_print(file, data)
                    self.Row.current.visible = False
                    self.Row.current.update()
                    page.close_dialog()

                page.dialog = ft.AlertDialog(True, ft.Text('Удаление'),
                                             content=ft.Row([
                                                 ft.Icon(
                                                     ft.icons.DELETE_FOREVER),
                                                 ft.Text(
                                                     "Вы хотите удалить эту запись?")
                                             ]),
                                             actions=[
                    ft.TextButton(
                        text='Да', icon=ft.icons.CHECK, on_click=delete_info),
                    ft.TextButton(text='Нет', icon=ft.icons.CANCEL,
                                  on_click=lambda e: self.__open_edit(page))
                ],
                    open=True
                )
                page.update()

            def render(self, page: ft.Page):
                return ft.DataRow([
                    ft.DataCell(ft.Text(self._Department)),
                    ft.DataCell(ft.Text(self._Name)),
                    ft.DataCell(ft.Text(self._Job_title)),
                    ft.DataCell(ft.Text(self._Age)),
                    ft.DataCell(ft.Text(self._Wage)),
                    ft.DataCell(ft.Text(''), show_edit_icon=True)
                ], on_select_changed=lambda e: self.__open_edit(page),
                    data=self.show(), ref=self.Row)

        def sort_columns(self, col):
            flage = False

            def on_sort(e: ft.ControlEvent):
                nonlocal flage
                self.ref.current.rows.sort(
                    key=lambda x: x.data[col], reverse=flage)
                flage = not flage
                self.ref.current.update()
            return on_sort

        def update(self, page: ft.Page):
            self.ref.current.rows = [i.render(page)
                                     for i in self.ref.current.data]
            self.ref.current.update()

        def render(self, page: ft.Page): return ft.DataTable([
            ft.DataColumn(label=ft.Text('Отдел', color='blue'),
                          on_sort=self.sort_columns('Department')),
            ft.DataColumn(label=ft.Text('ФИО', color='blue'),
                          on_sort=self.sort_columns('Name')),
            ft.DataColumn(label=ft.Text('Должность', color='blue'),
                          on_sort=self.sort_columns('Job_title')),
            ft.DataColumn(label=ft.Text('Возраст', color='blue'),
                          numeric=True, on_sort=self.sort_columns('Age')),
            ft.DataColumn(label=ft.Text('Заработная плата', color='blue'),
                          numeric=True, on_sort=self.sort_columns('Wage')),
            ft.DataColumn(ft.Icon(ft.icons.MODE_EDIT))
        ], border=ft.Border(ft.BorderSide(1, 'blue'), ft.BorderSide(1, 'blue'), ft.BorderSide(1, 'blue'), ft.BorderSide(1, 'blue')),
            horizontal_lines=ft.BorderSide(1, '#14324b'),
            vertical_lines=ft.BorderSide(1, 'blue'),
            rows=[i.render(page) for i in self.__data],
            border_radius=10, ref=self.ref,
            data=self.__data
        )

        def fill_update(self, page: ft.Page):
            self.ref.current.data = [self.__DataRow(
                i, obj) for i, obj in enumerate(file_reading(file))]
            self.update(page)

        def search(self, page: ft.Page, text: str, type: str):
            data = self.ref.current.data
            self.ref.current.data = [i for i in data if str(
                i.show()[type]).lower().find(text.lower()) != -1]
            self.update(page)

        def search_int(self, page: ft.Page, num1: int, num2: int, type: str):
            data = self.ref.current.data
            self.ref.current.data = [
                i for i in data if num1 <= i.show()[type] <= num2]
            self.update(page)

        def save(self, path_file: str):
            data = [i.show_text() for i in self.ref.current.data]
            with open(path_file, 'w', encoding='utf-8') as file:
                file.write('\n'.join(data))

    class __AppBar():
        def __init__(self) -> None:
            self.add = ft.IconButton(ft.icons.ADD, tooltip='Добавить')
            self.more = ft.IconButton(ft.icons.MORE_VERT, tooltip='Запросы')
            self.file_dir = ft.FilePicker()
            self.search_text = ft.TextField(
                label='Поиск по ФИО', icon=ft.icons.SEARCH, height=40)
            self.appbar = ft.AppBar(leading=ft.Icon(ft.icons.DATA_OBJECT), title=ft.Text('Таблица данных "Сотрудники"'), leading_width=40,
                                    actions=[
                                        self.search_text,
                                        ft.IconButton(ft.icons.SAVE, 'blue', on_click=lambda e: self.file_dir.save_file(
                                            allowed_extensions=['txt']), tooltip='Сохранение'),
                                        self.add,
                                        self.more,
            ])

    class __EndDrawer():
        def __init__(self, all_filters):
            self.filters = [
                ft.TextField(label='Название', scale=0.9,
                             on_change=all_filters),
                ft.TextField(label='2000-12-31', scale=0.9,
                             on_change=all_filters),
                ft.TextField(label='От', scale=0.8, input_filter=ft.NumbersOnlyInputFilter(
                ), on_change=all_filters),
                ft.TextField(label='До', scale=0.8, input_filter=ft.NumbersOnlyInputFilter(
                ), on_change=all_filters),
                ft.TextField(label='От', scale=0.8, input_filter=ft.NumbersOnlyInputFilter(
                ), on_change=all_filters),
                ft.TextField(label='До', scale=0.8, input_filter=ft.NumbersOnlyInputFilter(
                ), on_change=all_filters)
            ]
            self.draver = ft.NavigationDrawer([
                ft.Text('Запросы', text_align=ft.TextAlign.CENTER,
                        size=30, weight=700),
                ft.Column([
                    ft.Text(
                        'Производитель', text_align=ft.TextAlign.CENTER), self.filters[0],
                    ft.Text('Срок годности',
                            text_align=ft.TextAlign.CENTER), self.filters[1],
                    ft.Text(
                        'Цена', text_align=ft.TextAlign.CENTER), self.filters[2], self.filters[3],
                    ft.Text(
                        'Количество на складе', text_align=ft.TextAlign.CENTER), self.filters[4], self.filters[5],
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            ])

        def default(self, table):
            self.filters[0].value = None
            self.filters[1].value = None
            self.filters[2].value = min(
                [i.show()['Age'] for i in table.ref.current.data])
            self.filters[3].value = max(
                [i.show()['Age'] for i in table.ref.current.data])
            self.filters[4].value = min(
                [i.show()['Wage'] for i in table.ref.current.data])
            self.filters[5].value = max(
                [i.show()['Wage'] for i in table.ref.current.data])
