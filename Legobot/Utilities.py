# Legobot
# Copyright (C) 2016 Brenton Briggs, Kevin McCabe, and Drew Bronson


class Utilities():
    """
    Miscellaneous utilities for Legobot services
    """

    @staticmethod
    def tokenize(text):
        """
        Returns text split along newlines.

        Args:
            text (str): The text to be tokenized

        Returns:
            list: Text split along newlines
        """
        return text.split('\n')

    @staticmethod
    def truncate(text, length=255):
        """
        Splits the message into a list of strings of of length `length`

        Args:
            text (str): The text to be divided
            length (int, optional): The length of the chunks of text. \
                    Defaults to 255.

        Returns:
            list: Text divided into chunks of length `length`
        """

        lines = []
        i = 0
        while i < len(text) - 1:
            try:
                lines.append(text[i:i+length])
                i += length

            except IndexError as e:
                lines.append(text[i:])
        return lines

    @staticmethod
    def isNotEmpty(text):
        """
        Check if the given text is empty.

        Args:
            text (str): The text to assess

        Returns:
            bool: False if empty otherwise, True
        """

        return True if text else False
