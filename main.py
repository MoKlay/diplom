import flet as ft
from typing import Callable
from read import file_reading, file_print

file ='data.json'

class Main():
  def __init__(self, page: ft.Page) -> None:
    self.page = page
    self.__ref_alert = ft.Ref[ft.AlertDialog]()
    self.__alert = self.__Alert(self.__ref_alert, self.page.close_dialog, self.page)
    self.__table = self.__DataTable(self.__alert.edit_render)
    self.__appbar = self.__AppBar(self.__table,self.page)
    self.__login = self.__Login(self, self.panel_info, self.user_info)
    self.__dialog = ft.AlertDialog(ref=self.__ref_alert)
    self.__end_draver = self.__EndDrawer(self.__table.search, self.__table.search_int)
    self.render()
    

  def render(self):
    self.page.fonts = {
      'Robobo': 'https://fonts.googleapis.com/css2?family=Roboto:ital,wght@0,100;0,300;0,400;0,500;0,700;0,900;1,100;1,300;1,400;1,500;1,700;1,900&display=swap'
    }
    self.page.title = 'Аптека "7 жизней"'
    self.page.adaptive = True
    self.page.scroll = True
    self.page.window_min_width = 1000
    self.page.window_min_height = 500
    self.page.adaptive = True
    self.__login.render()
    self.page.window_center()

  def panel_info(self):
    self.page.add(ft.Column([self.__table.render()], horizontal_alignment=ft.CrossAxisAlignment.STRETCH))
    self.page.dialog = self.__dialog
    self.page.appbar = self.__appbar.appbar
    self.page.floating_action_button = ft.FloatingActionButton(icon=ft.icons.ADD, on_click= lambda e: {self.__alert.add_render(self.__table.update)}, bgcolor='green')
    self.page.end_drawer = self.__end_draver.draver
    self.__table.update()

  def user_info(self):
    self.__table.calback = self.__alert.user_alert
    self.page.add(ft.Column([self.__table.render()], horizontal_alignment=ft.CrossAxisAlignment.STRETCH))
    self.page.dialog = self.__dialog
    self.page.appbar = self.__appbar.appbar
    self.page.end_drawer = self.__end_draver.draver
    self.__table.update()
    self.__end_draver.default()
    
  class __Login():
    def __init__(self, main, admin: Callable, user: Callable) -> None:
      self.__admin = admin
      self.__user = user
      self.__main = main
      self.user_login = ft.TextField(label='Логин', width=240)
      self.__user_pass = ft.TextField(
          label='Пароль', width=240, password=True, can_reveal_password=True,)
      self.__btn_verif = ft.TextButton('Вход', width=100, disabled=True)

    def __validate(self, e) -> None:
      if all([self.user_login.value, self.__user_pass.value]):
        self.__btn_verif.disabled = False
      else:
        self.__btn_verif.disabled = True
      self.__btn_verif.update()
      
    def __verication(self, e): 
      self.__main.page.close_dialog()
      if self.user_login.value.strip() == 'admin' and self.__user_pass.value.strip() == 'admin':
        self.__admin()
      else:
        self.__user()
      self.__main.page.update()
    
    def render(self):
      self.user_login.on_change = self.__validate
      self.__user_pass.on_change = self.__validate
      
      self.__user_pass.on_submit = self.__verication
      self.__btn_verif.on_click = self.__verication
      
      self.__main.page.dialog = ft.AlertDialog(True, ft.Text('Авторизация'),
                                         ft.Column([self.user_login, self.__user_pass], height=150,
                                                   alignment=ft.MainAxisAlignment.CENTER), [self.__btn_verif],
                                         actions_alignment=ft.MainAxisAlignment.CENTER, open=True)
      self.__main.page.update()
      
      self.__main.page.snack_bar = ft.SnackBar(ft.Text(
        'Неверные данные входа', color='red', text_align=ft.TextAlign.CENTER), bgcolor='white')
      
      self.user_login.on_submit = lambda e: self.__user_pass.focus()
      self.user_login.focus()
      
  class __Alert():
    def __init__(self, ref: ft.Ref[ft.AlertDialog], close: Callable, page: ft.Page) -> None:
      self.__page = page
      self.__ref = ref
      self.__input = [
        ft.TextField(label='Название'),
        ft.TextField(label='Производитель'),
        ft.TextField(label='Цена', input_filter=ft.NumbersOnlyInputFilter()),
        ft.TextField(label='Срок годности'),
        ft.TextField(label='Количество на складе',
                    input_filter=ft.NumbersOnlyInputFilter())
      ]
      
      self.close = close

      
    def add_render(self, updata: Callable):
      for i in self.__input: i.value = None
      self.__ref.current.title = ft.Text('Добавление')
      self.__ref.current.content = ft.Column(self.__input, height=350)
      self.__ref.current.actions = [
        ft.TextButton(text='Добавить', icon=ft.icons.ADD, on_click=lambda e: self.__pick('add', updata)),
        ft.TextButton(text='Отмена', icon=ft.icons.CANCEL, on_click=lambda e: self.close())
      ]
      self.__ref.current.open = True
      self.__ref.current.update()
    
    def edit_render(self, updata: Callable, id:int, list: list = None):
      if not list is None:
        for i in range(5): self.__input[i].value = list[i]
      self.__ref.current.title = ft.Text('Редактирование')
      self.__ref.current.content = ft.Column(self.__input, height=350)
      self.__ref.current.actions = [
        ft.TextButton(text='Сохранить', icon=ft.icons.SAVE, on_click=lambda e:self.__pick( 'edit', updata,id)),
        ft.TextButton(text='Отмена', icon=ft.icons.CANCEL, on_click=lambda e: self.close()),
        ft.TextButton(text='Удалить', icon=ft.icons.DELETE, on_click=lambda e: self.__delete_val(updata, id), icon_color='red', style=ft.ButtonStyle('red'))
      ]
      self.__ref.current.open = True
      self.__ref.current.update()
    
    def __delete_val(self,updata: Callable, id):
      self.__ref.current.title = ft.Text('Удаление')
      self.__ref.current.content = ft.Row([ft.Icon(ft.icons.DELETE_FOREVER),ft.Text("Вы хотите удалить эту запись?")])
      self.__ref.current.actions = [
                    ft.TextButton(text='Да', icon=ft.icons.CHECK, on_click=lambda e: self.__pick( 'delete', updata,id)),
                    ft.TextButton(text='Нет', icon=ft.icons.CANCEL, on_click=lambda e: self.edit_render(updata, id))
                
                ]
      self.__ref.current.update()
      
    def __pick(self,  event, updata, id=None):
      if event == 'delete':
        data = file_reading(file)
        data.pop(id)
        file_print(file, data)
      else: 
        info = [i.value for i in self.__input]
        if all(info):
          if event == 'edit':
            data = file_reading(file)
            data[id] = {
              'Название': info[0],
              'Производитель': info[1],
              'Цена': info[2],
              'Срок годности': info[3],
              'Количество на складе': info[4]
            }
            file_print(file, data)
          elif event == 'add':
            data = file_reading(file)
            data.append({
                "Название": info[0],
                "Производитель": info[1],
                "Цена": info[2],
                "Срок годности": info[3],
                "Количество на складе": info[4]
            })
            file_print(file, data)
      self.close()
      updata()
      
    
    def user_alert(self,updata=None, id=None, dsd=None):
      self.__ref.current.title = ft.Text('Заказ товара')
      self.__ref.current.content = ft.Row([
        ft.Icon(ft.icons.QUESTION_ANSWER_OUTLINED),
        ft.Text('Заказать товар?')
      ])
      def ok(e):
        self.close()
        self.__page.snack_bar = ft.SnackBar(ft.Text('Товар был успешно заказан!!!'), True)
        self.__page.update()
      self.__ref.current.actions=[
        ft.TextButton('Заказать', ft.icons.CHECK, style=ft.ButtonStyle('green'), on_click=ok),
        ft.TextButton('Отмена', ft.icons.CANCEL_SCHEDULE_SEND_OUTLINED, style=ft.ButtonStyle('red'), on_click=lambda e: self.close())
      ]
      self.__ref.current.open = True
      self.__ref.current.update()
  class __AppBar():
    def __init__(self, table, page:ft.Page) -> None:
      self.search_text = ft.TextField(label='Поиск', height=40, adaptive=True)
      self.search_text.on_change = lambda e: table.search(self.search_text.value, 'Название')
      self.appbar = ft.AppBar(leading=ft.Image('/favicon.png', width=300, height=300),
                              title=ft.Text('Аптека\n7 жизней', color='green', weight=ft.FontWeight.W_900, size=25),
                              actions=[
                                  self.search_text,
                                  ft.IconButton(ft.icons.MORE_VERT, tooltip='Запросы', on_click=lambda e: page.show_end_drawer(page.end_drawer)),
      ], adaptive=True,automatically_imply_leading=True)
     
  class __EndDrawer():
    def __init__(self, str, int):
      self.__int = int
      self.__str = str
      self.filters = [
        ft.TextField(label='Название', scale=0.9),
        ft.TextField(label='2000-12-31', scale=0.9),
        ft.TextField(label='От', scale=0.8, input_filter=ft.NumbersOnlyInputFilter()),
        ft.TextField(label='До', scale=0.8, input_filter=ft.NumbersOnlyInputFilter()),
        ft.TextField(label='От', scale=0.8, input_filter=ft.NumbersOnlyInputFilter()),
        ft.TextField(label='До', scale=0.8, input_filter=ft.NumbersOnlyInputFilter())
      ]
      self.draver = ft.NavigationDrawer([
        ft.Text('Запросы', text_align=ft.TextAlign.CENTER, size=30, weight=700),
        ft.Column([
            ft.Text('Производитель', text_align=ft.TextAlign.CENTER), self.filters[0],
            ft.Text('Срок годности',text_align=ft.TextAlign.CENTER), self.filters[1],
            ft.Text('Цена', text_align=ft.TextAlign.CENTER), self.filters[2], self.filters[3],
            ft.Text('Количество на складе', text_align=ft.TextAlign.CENTER), self.filters[4], self.filters[5],
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
      ])
      
    def default(self):
      self.filters[0].on_change = lambda e: self.__str(self.filters[0].value, 'Производитель')
      self.filters[1].on_change = lambda e: self.__str(self.filters[1].value, 'Срок годности')
      self.filters[2].on_change = lambda e: self.__int(self.filters[2].value, self.filters[3].value,'Цена')
      self.filters[3].on_change = lambda e: self.__int(self.filters[2].value, self.filters[3].value,'Цена')
      self.filters[4].on_change = lambda e: self.__int(self.filters[4].value, self.filters[5].value,'Количество на складе')
      self.filters[5].on_change = lambda e: self.__int(self.filters[4].value, self.filters[5].value,'Количество на складе')
      


  
  
  class __DataTable():
        def __init__(self, open:Callable) -> None:
            self.ref = ft.Ref[ft.DataTable]()
            self.calback = open
        class __Product():
            def __init__(self, obj: object) -> None:
              self.__obj = obj
              self.__name = obj['Название']
              self.__manufacturer = obj['Производитель']
              self.__price = obj['Цена']
              self.__expiration_date = obj['Срок годности']
              self.__stock_quantity = obj['Количество на складе']

            def update_obj(self,obj: object):
              self.__obj = obj
              self.__name = obj['Название']
              self.__manufacturer = obj['Производитель']
              self.__price = obj['Цена']
              self.__expiration_date = obj['Срок годности']
              self.__stock_quantity = obj['Количество на складе']
            
            def show(self): return self.__obj

            def show_text(self):
                return str(self.__name).ljust(40) + str(self.__manufacturer).ljust(15) + str(
                    self.__price).ljust(40) + str(self.__expiration_date).rjust(5) + str(self.__stock_quantity).rjust(8)
            
            def show_mass(self):
              return [
                self.__name,
                self.__manufacturer,
                self.__price,
                self.__expiration_date,
                self.__stock_quantity
              ]
                

        class __DataRow(__Product):
            def __init__(self, id:int, obj: object) -> None:
                super().__init__(obj)
                self.__id = id
                self.__Row = ft.Ref[ft.DataRow]()
                

            def render(self, open: Callable, updata: Callable):
                return ft.DataRow([
                    ft.DataCell(ft.Text(self.show()['Название'])),
                    ft.DataCell(ft.Text(self.show()['Производитель'])),
                    ft.DataCell(ft.Text(self.show()['Цена'])),
                    ft.DataCell(ft.Text(self.show()['Срок годности'])),
                    ft.DataCell(ft.Text(self.show()['Количество на складе']))
                ], on_select_changed=lambda e: open(updata, self.__id, self.show_mass()), ref=self.__Row, data=self.show())

        def sort_columns(self, col):
            flage = False
            def on_sort(e: ft.ControlEvent):
                nonlocal flage
                self.ref.current.rows.sort(key=lambda x: x.data[col], reverse=flage)
                flage = not flage
                self.ref.current.update()
            return on_sort

        def update(self, data=None):
          if data is None:
            data = file_reading(file)
          self.ref.current.rows = [self.__DataRow(i, obj).render(self.calback, self.update) for i, obj in enumerate(data)]
          self.ref.current.update()

        def render(self): return ft.DataTable([
            ft.DataColumn(label=ft.Text('Название', color='green', size=30, weight=ft.FontWeight.W_500),on_sort=self.sort_columns('Название')),
            ft.DataColumn(label=ft.Text('Производитель', color='green', size=30, weight=ft.FontWeight.W_500),on_sort=self.sort_columns('Производитель')),
            ft.DataColumn(label=ft.Text('Цена', color='green', size=30, weight=ft.FontWeight.W_500),on_sort=self.sort_columns('Цена')),
            ft.DataColumn(label=ft.Text('Срок годности', color='green', size=30, weight=ft.FontWeight.W_500),numeric=True, on_sort=self.sort_columns('Срок годности')),
            ft.DataColumn(label=ft.Text('Количество на складе', color='green', size=30, weight=ft.FontWeight.W_500),numeric=True, on_sort=self.sort_columns('Количество на складе'))
          ], border=ft.Border(ft.BorderSide(1, 'green'), ft.BorderSide(1, 'green'), ft.BorderSide(1, 'green'), ft.BorderSide(1, 'green')),
          horizontal_lines=ft.BorderSide(1, '#020'),
          vertical_lines=ft.BorderSide(1, 'green'),
          border_radius=10, ref=self.ref, data_text_style=ft.TextStyle(20)
        )

        def search(self, text: str, type: str):
            data = file_reading(file)
            self.update([i for i in data if i[type].lower().find(text.lower()) != -1])

        def search_int(self, num1, num2, type: str):
            data = file_reading(file)
            if num1 == '':num1 =min([int(i[type]) for i in file_reading(file)])
            if num2 == '': num2 =max([int(i[type]) for i in file_reading(file)])
            self.update([i for i in data if int(num1) <= int(i[type]) <= int(num2)])

        
        
        def save(self, path_file: str, data=None):
            if data is None:
              data = [i.show_text() for i in self.ref.current.data]
            with open(path_file, 'w', encoding='utf-8') as file:
                file.write('\n'.join(data))