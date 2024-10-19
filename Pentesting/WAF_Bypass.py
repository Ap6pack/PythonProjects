from burp import IBurpExtender, IContextMenuFactory, IExtensionHelpers
from burp import IContextMenuInvocation
from javax.swing import JMenuItem, JOptionPane
import random
import string

class BurpExtender(IBurpExtender, IContextMenuFactory):

    def registerExtenderCallbacks(self, callbacks):
        # Set up the extension
        self._callbacks = callbacks
        self._helpers = callbacks.getHelpers()
        callbacks.setExtensionName("Add Random Text Extension")

        # Register the context menu factory
        callbacks.registerContextMenuFactory(self)

    def createMenuItems(self, invocation):
        menu_items = []

        # Add context menu item for request editor context
        if invocation.getInvocationContext() == IContextMenuInvocation.CONTEXT_MESSAGE_EDITOR_REQUEST:
            menu_item = JMenuItem("Add Random Text to Request", actionPerformed=lambda x, inv=invocation: self.addTextToRequest(inv))
            menu_items.append(menu_item)

        return menu_items

    def addTextToRequest(self, invocation):
        # Ensure we are working with a request editor context
        if invocation.getInvocationContext() != IContextMenuInvocation.CONTEXT_MESSAGE_EDITOR_REQUEST:
            self._callbacks.printError("This option is only available for request editors.")
            return

        selected_message = invocation.getSelectedMessages()[0]
        request_info = self._helpers.analyzeRequest(selected_message)

        # Prompt user for the amount of kilobytes they want to insert
        kb_input = JOptionPane.showInputDialog("Enter the number of KB to insert:")
        try:
            kb = int(kb_input)
            if kb <= 0:
                raise ValueError("The KB size must be greater than 0.")
        except ValueError:
            self._callbacks.printError("Invalid input. Please enter a valid number.")
            return

        # Generate random letters based on the user input (1 KB = 1024 bytes) using random.choice()
        text_size = kb * 1024
        text_data = "bullet='{}'".format(''.join([random.choice(string.ascii_letters) for _ in range(text_size)]))

        # Get the current request in bytes and convert it to a string
        original_request = selected_message.getRequest()
        original_request_str = self._helpers.bytesToString(original_request)

        # Get the selection bounds (cursor position) in the request editor
        selection_bounds = invocation.getSelectionBounds()

        if selection_bounds:
            # If there is a selection, insert the generated text at the selected position
            cursor_start = selection_bounds[0]
            cursor_end = selection_bounds[1]
        else:
            # If no selection is made, insert the text at the end of the request
            cursor_start = len(original_request_str)
            cursor_end = len(original_request_str)

        # Insert the random text into the request string
        modified_request_str = original_request_str[:cursor_start] + text_data + original_request_str[cursor_end:]

        # Convert the modified request back to bytes
        modified_request = self._helpers.stringToBytes(modified_request_str)

        # Update the request with the modified text
        selected_message.setRequest(modified_request)
