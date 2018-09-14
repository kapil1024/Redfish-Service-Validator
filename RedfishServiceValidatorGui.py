# Copyright Notice:
# Copyright 2016-2018 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Service-Validator/blob/master/LICENSE.md

"""
Redfish Service Validator GUI

File : RedfishServiceValidatorGui.py

Brief : This file contains the GUI to interact with the RedfishServiceValidator
"""

import configparser
import os
import sys
import threading
import tkinter as tk
from tkinter import filedialog as tkFileDialog
import traceback
import webbrowser

import RedfishLogo as logo
import RedfishServiceValidator as rsv

g_config_file_name = "config.ini"
g_config_defaults = {
    "SystemInformation": {
        "TargetIP": {
            "value": "127.0.0.1:8000",
            "description": "The IPv4 address of the system under test"
        },
        "SystemInfo": {
            "value": "Test Config, place your own description of target system here",
            "description": "A string to describe the system"
        },
        "UserName": {
            "value": "xuser",
            "description": "The user ID of the administrator on the system"
        },
        "Password": {
            "value": "xpasswd",
            "description": "The password of the administrator on the system"
        },
        "AuthType": {
            "value": "Basic",
            "description": "The type of authorization to use while testing",
            "options": ( "None", "Basic", "Session", "Token" )
        },
        "ForceAuth": {
            "value": "False",
            "description": "Force authentication on unsecure connections",
            "options": ( "True", "False" )
        },
        "Token": {
            "value": "",
            "description": "The token to use when AuthType is set to Token"
        },
        "UseSSL": {
            "value": "True",
            "description": "If SSL should be used while testing",
            "options": ( "True", "False" )
        },
        "CertificateCheck": {
            "value": "False",
            "description": "If validation of the SSL certificate should be performed",
            "options": ( "True", "False" )
        },
        "CertificateBundle": {
            "value": "",
            "description": "The location (file or directory) with certificates of trusted CAs"
        }
    },
    "Options": {
        "MetadataFilePath": {
            "value": "./SchemaFiles/metadata",
            "description": "Points to the local location of the DMTF schema files"
        },
        "Schema_Pack": {
            "value": "",
            "description": "URL path to a zipped pack of DMTF Schema; for LocalMode only"
        },
        "OemCheck": {
            "value": "True",
            "description": "Enable or disable validation of OEM objects",
            "options": ( "True", "False" )
        },
        "UriCheck": {
            "value": "False",
            "description": "Enable or disable validation of URIs for resources",
            "options": ( "True", "False" )
        },
        "CacheMode": {
            "value": "Off",
            "description": "Cache options for overriding or falling back to a file",
            "options": ( "Off", "Prefer", "Fallback" )
        },
        "CacheFilePath": {
            "value": "",
            "description": "The path to the cache directory"
        },
        "SchemaSuffix": {
            "value": "_v1.xml",
            "description": "The file suffix to append when searching for schema files"
        },
        "Timeout": {
            "value": "30",
            "description": "Interval of time before timing out on an HTTP request"
        },
        "HttpProxy": {
            "value": "",
            "description": "The proxy for HTTP requests to external URLs (not for the system under test)"
        },
        "HttpsProxy": {
            "value": "",
            "description": "The proxy for HTTPS requests to external URLs (not for the system under test)"
        },
        "LocalOnlyMode": {
            "value": "False",
            "description": "Only test properties against schema placed in the root of MetadataFilePath",
            "options": ( "True", "False" )
        },
        "ServiceMode": {
            "value": "False",
            "description": "Only test properties against resources/schema that exist on the service",
            "options": ( "True", "False" )
        },
        "LinkLimit": {
            "value": "LogEntry:20",
            "description": "Limits the amount of links accepted from collections"
        },
        "Sample": {
            "value": "0",
            "description": "The number of random members from large collections to validate; 0 = validate everything"
        }
    },
    "Validator": {
        "PayloadMode": {
            "value": "Default",
            "description": "Controls traversal of the service, or if local files are to be used",
            "options": ( "Default", "Tree", "Single", "TreeFile", "SingleFile" )
        },
        "PayloadFilePath": {
            "value": "",
            "description": "The path to a specific URI or file to validate"
        },
        "LogPath": {
            "value": "./logs",
            "description": "The folder where to place the output log files"
        }
    }
}

class RSVGui:
    """
    Main class for the GUI

    Args:
        parent (tkinter): Parent Tkinter object
    """

    def __init__( self, parent ):
        # Set up the configuration
        self.config = {}
        for section in g_config_defaults:
            self.config[section] = {}
            for option in g_config_defaults[section]:
                self.config[section][option] = g_config_defaults[section][option]

        # Read in the config file, and apply any valid settings
        self.config_file = g_config_file_name
        self.system_under_test = tk.StringVar()
        self.parse_config()

        # Initialize the window
        self.parent = parent
        self.parent.title( "Redfish Service Validator {}".format( rsv.tool_version ) )

        # Add the menubar
        menu_bar = tk.Menu( self.parent )
        file_menu = tk.Menu( menu_bar, tearoff = 0 )
        file_menu.add_command( label = "Open Config", command = self.open_config )
        file_menu.add_command( label = "Save Config", command = self.save_config )
        file_menu.add_command( label = "Save Config As", command = self.save_config_as )
        file_menu.add_command( label = "Edit Config", command = self.edit_config )
        file_menu.add_separator()
        file_menu.add_command( label = "Exit", command = self.parent.destroy )
        menu_bar.add_cascade( label = "File", menu = file_menu )
        self.parent.config( menu = menu_bar )

        # Add the logo
        image = tk.PhotoImage( data = logo.logo )
        label = tk.Label( self.parent, image = image, width = 384 )
        label.image = image
        label.pack( side = tk.TOP )

        # Add the system under test label
        tk.Label( self.parent, textvariable = self.system_under_test, font = ( None, 12 ) ).pack( side = tk.TOP )

        # Add the buttons
        button_frame = tk.Frame( self.parent )
        button_frame.pack( side = tk.TOP, fill = tk.X )
        self.run_button_text = tk.StringVar()
        self.run_button_text.set( "Run Test" )
        self.run_button = tk.Button( button_frame, textvariable = self.run_button_text, command = self.run )
        self.run_button.pack( side = tk.LEFT )
        self.run_label_text = tk.StringVar()
        self.run_label_text.set( "" )
        tk.Label( button_frame, textvariable = self.run_label_text ).pack( side = tk.LEFT )
        tk.Button( button_frame, text = "Exit", command = self.parent.destroy ).pack( side = tk.RIGHT )

    def update_sut( self ):
        """
        Updates the System Under Test string
        """
        self.system_under_test.set( "System Under Test: " + self.config["SystemInformation"]["TargetIP"]["value"] )

    def parse_config( self ):
        """
        Parses the configuration settings from a file
        """
        config_parser = configparser.ConfigParser()
        config_parser.optionxform = str
        config_parser.read( self.config_file )
        for section in config_parser.sections():
            for option in config_parser.options( section ):
                if section in self.config:
                    if option in self.config[section]:
                        self.config[section][option]["value"] = config_parser.get( section, option )
        self.update_sut()

    def build_config_parser( self, preserve_case ):
        """
        Builds a config parser element from the existing configuration

        Args:
            preserve_case (bool): True if the casing of the options is to be preserved

        Returns:
            ConfigParser: A ConfigParser object generated from the configuration data
        """
        config_parser = configparser.ConfigParser()
        if preserve_case == True:
            config_parser.optionxform = str
        for section in self.config:
            config_parser.add_section( section )
            for option in self.config[section]:
                config_parser.set( section, option, self.config[section][option]["value"] )
        return config_parser

    def open_config( self ):
        """
        Opens the configuration settings from a file
        """
        filename = tkFileDialog.askopenfilename( initialdir = os.getcwd(), title = "Open", filetypes = ( ( "INI", "*.ini" ), ( "All Files", "*.*" ) ) )
        if filename == "":
            # User closed the box; just return
            return
        self.config_file = filename
        self.parse_config()

    def edit_config( self ):
        """
        Edits the configuration settings
        """
        option_win = tk.Toplevel()
        config_values = {}

        # Iterate through the config file options to build the window
        for section in self.config:
            config_values[section] = {}
            section_frame = tk.Frame( option_win )
            section_frame.pack( side = tk.TOP )
            tk.Label( section_frame, text = section, anchor = "center", font = ( None, 16 ) ).pack( side = tk.LEFT )
            for option in self.config[section]:
                option_frame = tk.Frame( option_win )
                option_frame.pack( side = tk.TOP, fill = tk.X )
                tk.Label( option_frame, text = option, width = 16, anchor = "w" ).pack( side = tk.LEFT )
                config_values[section][option] = tk.StringVar()
                config_values[section][option].set( self.config[section][option]["value"] )
                if "options" in self.config[section][option]:
                    option_menu = tk.OptionMenu( option_frame, config_values[section][option], *self.config[section][option]["options"] )
                    option_menu.configure( width = 26 )    # Need a better way to fine tune this so it lines up nicely with the text boxes
                    option_menu.pack( side = tk.LEFT )
                else:
                    tk.Entry( option_frame, width = 32, textvariable = config_values[section][option] ).pack( side = tk.LEFT )
                tk.Label( option_frame, text = self.config[section][option]["description"], anchor = "w" ).pack( side = tk.LEFT )
        tk.Button( option_win, text = "Apply", command = lambda: self.apply_config( option_win, config_values ) ).pack( side = tk.BOTTOM )

    def apply_config( self, window, config_values ):
        """
        Applies the configation settings from the edit window

        Args:
            window (Toplevel): Tkinter Toplevel object with text boxes to apply
            config_values (Array): An array of StringVar objects with the user input
        """
        for section in self.config:
            for option in self.config[section]:
                self.config[section][option]["value"] = config_values[section][option].get()
        self.update_sut()
        window.destroy()

    def save_config( self ):
        """
        Saves the config file
        """
        config_parser = self.build_config_parser( True )
        with open( self.config_file, "w" ) as config_file:
            config_parser.write( config_file )

    def save_config_as( self ):
        """
        Saves the config file as a new file
        """
        filename = tkFileDialog.asksaveasfilename( initialdir = os.getcwd(), title = "Save As", filetypes = ( ( "INI", "*.ini" ), ( "All Files", "*.*" ) ) )
        if filename == "":
            # User closed the box; just return
            return
        self.config_file = filename
        if self.config_file.lower().endswith( ".ini" ) == False:
            self.config_file = self.config_file + ".ini"
        self.save_config()

    def run( self ):
        """
        Runs the service validator
        """
        self.run_button_text.set( "Running" )
        self.run_button.config( state = tk.DISABLED )
        run_thread = threading.Thread( target = self.run_imp )
        run_thread.daemon = True
        run_thread.start()

    def run_imp( self ):
        """
        Thread for running the service validator so the GUI doesn't freeze
        """
        self.run_label_text.set( "Test running; please wait" )

        run_window = tk.Toplevel()
        run_text_frame = tk.Frame( run_window )
        run_text_frame.pack( side = tk.TOP )
        run_scroll = tk.Scrollbar( run_text_frame )
        run_scroll.pack( side = tk.RIGHT, fill = tk.Y )
        run_text = tk.Text( run_text_frame, height = 48, width = 128, yscrollcommand = run_scroll.set )
        rsv.rsvLogger.handlers[0].stream = RunOutput( run_text )
        run_text.pack( side = tk.TOP )
        run_button_frame = tk.Frame( run_window )
        run_button_frame.pack( side = tk.BOTTOM )
        tk.Button( run_button_frame, text = "OK", command = run_window.destroy ).pack( side = tk.LEFT )
        tk.Button( run_button_frame, text = "Copy", command = lambda: self.copy_text( run_text ) ).pack( side = tk.RIGHT )

        # Launch the validator
        try:
            rsv_config = self.build_config_parser( False )
            status_code, last_results_page, exit_string = rsv.main(direct_parser = rsv_config )
            if last_results_page != None:
                webbrowser.open_new( last_results_page )
            else:
                # The validation could not take place (for a controlled reason)
                notification_window = tk.Toplevel()
                tk.Label( notification_window, text = "Test aborted: " + exit_string, anchor = "center" ).pack( side = tk.TOP )
                tk.Button( notification_window, text = "OK", command = notification_window.destroy ).pack( side = tk.BOTTOM )
        except:
            oops_window = tk.Toplevel()
            tk.Label( oops_window, text = "Please copy the info below and file an issue on GitHub!", width = 64, anchor = "center" ).pack( side = tk.TOP )
            oops_text_frame = tk.Frame( oops_window )
            oops_text_frame.pack( side = tk.TOP )
            oops_scroll = tk.Scrollbar( oops_text_frame )
            oops_scroll.pack( side = tk.RIGHT, fill = tk.Y )
            oops_text = tk.Text( oops_text_frame, height = 32, width = 64, yscrollcommand = oops_scroll.set )
            oops_text.insert( tk.END, traceback.format_exc() )
            oops_text.pack( side = tk.TOP )
            oops_button_frame = tk.Frame( oops_window )
            oops_button_frame.pack( side = tk.BOTTOM )
            tk.Button( oops_button_frame, text = "OK", command = oops_window.destroy ).pack( side = tk.LEFT )
            tk.Button( oops_button_frame, text = "Copy", command = lambda: self.copy_text( oops_text ) ).pack( side = tk.RIGHT )
        self.run_button.config( state = tk.NORMAL )
        self.run_button_text.set( "Run Test" )
        self.run_label_text.set( "Test Complete" )

    def copy_text( self, text ):
        """
        Copies text to the system clipboard

        Args:
            text (Text): Tkinter Text object with text to copy
        """
        self.parent.clipboard_clear()
        self.parent.clipboard_append( text.get( 1.0, tk.END ) )

class RunOutput( object ):
    """
    Runtime output class

    Args:
        text (Text): Tkinter Text object to use as the output
    """

    def __init__( self, text ):
        self.output = text

    def write( self, string ):
        """
        Writes to the output object

        Args:
            string (string): The string to output
        """
        if self.output.winfo_exists():
            self.output.insert( tk.END, string )
            self.output.see( tk.END )

def main():
    """
    Entry point for the GUI
    """
    root = tk.Tk()
    gui = RSVGui( root )
    root.mainloop()

if __name__ == '__main__':
    main()
