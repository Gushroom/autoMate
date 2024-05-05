from pages.edit_action_list_view import ActionList
from pages.edit_function_page import FunctionListView
from utils.global_util import GlobalUtil
from utils.qt_util import QtUtil
from PyQt6.QtWidgets import QMainWindow, QLabel
from PyQt6.QtCore import pyqtSignal, Qt



interface_ui = QtUtil.load_ui_type("edit_page.ui")
   

class EditPage(QMainWindow, interface_ui):
    # 页面关闭的信号
    page_closed = pyqtSignal(str)

    
    def __init__(self, func_status, func_list_pos_row, func_list_pos_column, output_save_dict=None, action_list: ActionList = None, func_name="默认名称", func_description="无"):
        self.func_list_pos_column = func_list_pos_column
        self.func_list_pos_row = func_list_pos_row
        # 属于通用还是专属
        self.func_status = func_status
        self.func_description = func_description
        # 在func上的名称
        self.func_name = func_name
        if not output_save_dict:
            output_save_dict = {}
        # 保存action的输出结果
        self.output_save_dict = output_save_dict
        if not action_list:
            action_list = ActionList(parent=self)
        self.action_list = action_list
        super().__init__()
        self.setupUi(self)
        self.setup_up()

    def closeEvent(self, event):
        self.page_closed.emit(self.func_name)

    def dump(self):
        return {"func_list_pos_column": self.func_list_pos_column,
                "func_list_pos_row": self.func_list_pos_row,
                "func_name": self.func_name,
                "func_status": self.func_status,
                "func_description": self.func_description,
                # 只保存结果名，不保存输出的结果值
                "output_save_dict_keys": list(self.output_save_dict.keys()),
                "action_list": self.action_list.dump()
                }

    def setup_up(self):
        self.func_name_edit.setText(self.func_name)
        self.func_description_edit.setText(self.func_description)
        function_list_view = FunctionListView()
        self.function_list_layout.addWidget(function_list_view)
        self.action_list_view_layout.addWidget(self.action_list)
        self.run_button.clicked.connect(self.run_action)
        self.save_button.clicked.connect(self.__save_button_click)
        self.cancel_button.clicked.connect(self.__cancel_button_click)
        # 设置间距
        self.action_list_view_layout.setStretch(0, 1)
        self.action_list_view_layout.setStretch(1, 2)
        self.action_list_view_layout.setStretch(2, 10)
        # 设置居上对齐
        self.run_output_layout.setAlignment(Qt.AlignmentFlag.AlignTop)


    def run_output_ui(self):
        i = 0
        for output in self.output_save_dict:
            self.run_output_layout.addWidget(QLabel(output), i, 0)
            self.run_output_layout.addWidget(QLabel(" : "), i, 1) 
            self.run_output_layout.addWidget(QLabel(str(self.output_save_dict[output])), i, 2) 
            i += 1       

    def __save_button_click(self):
        self.func_name = self.func_name_edit.text()
        self.func_description = self.func_description_edit.text()
        GlobalUtil.edit_page_global.append(self)
        GlobalUtil.save_to_local()
        self.close()


    def __cancel_button_click(self):
        # GlobalUtil.delete_edit_page(GlobalUtil.current_page)
        self.close()


    def run_action(self, s:str):
        for index in range(self.action_list.count()):
            func = self.action_list.item(index)
            res = func.action.run_with_out_arg()
            self.run_output_ui()
        return "执行成功！"


    def get_chain(self):
        chain = []
        for index in range(self.action_list.count()):
            func = self.action_list.item(index)
            chain.append(func.__getattribute__("get_action")().convert_langchain_tool())
        return chain


    @staticmethod
    def global_load():
        # 从本地缓存数据读取数据
        edit_pages_json = GlobalUtil.read_from_local()
        for edit_page_json in edit_pages_json:
            from pages.edit_page import EditPage
            from pages.edit_action_list_view import ActionList
            action_list = ActionList.load(edit_page_json["action_list"])
            edit_page = EditPage(
                func_status=edit_page_json["func_status"],
                func_list_pos_row=edit_page_json["func_list_pos_row"],
                func_list_pos_column=edit_page_json["func_list_pos_column"],
                func_name = edit_page_json["func_name"],
                func_description = edit_page_json["func_description"],
                action_list=action_list,
                # 保存结果输出变量名，运行结果只有在运行时才会被保存
                output_save_dict={i: None for i in edit_page_json["output_save_dict_keys"]}
                )
            action_list.setParent(edit_page)
            edit_page.func_name = edit_page_json["func_name"]
            edit_page.func_description = edit_page_json["func_description"]
            GlobalUtil.edit_page_global.append(edit_page)


    @staticmethod
    def get_edit_page_by_position(func_status, row, column):
        for i in GlobalUtil.edit_page_global:
            if i.func_list_pos_row == row and i.func_list_pos_column == column \
                    and i.func_status == func_status:
                return i
        return None
    
    @staticmethod
    def delete_edite_page(edit_page):
        GlobalUtil.edit_page_global.remove(edit_page)
        GlobalUtil.save_to_local()
        
