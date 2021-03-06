import sys
import pandas as pd
from sqlalchemy import create_engine

def load_data(messages_filepath, categories_filepath):
    """
    Loads and combines messages and catgeories data.
    
    Args:
        messages_filepath (string): filepath for messages data.
        categories_filepath (string): filepath for categories data.
    
    Returns:
        df (pandas dataframe): 
    
    """
    
    messages = pd.read_csv(messages_filepath)
    categories = pd.read_csv(categories_filepath)
    df = pd.merge(messages, categories, left_on='id', right_on='id', how='inner')
    
    categories = categories['categories'].str.split(';', expand=True)

    row = categories.iloc[0,:]

    category_colnames = row.apply(lambda x : x[:-2])
    categories.columns = category_colnames
    for column in categories:
        categories[column] = categories[column].str[-1:]
        categories[column] = categories[column].astype(int)
        
    df.drop(columns='categories', axis=1, inplace=True)
    df = pd.concat([df, categories], axis=1, join='inner')
    return(df)
    
def clean_data(df):
    """
    Remove duplicates and replaces incorrect values in the abelled messages data.
    
    Args:
        df (pandas dataframe): labelled message data.
    
    Returns:
        df (pandas dataframe): cleaned message data.
    """
    
    df = df.drop_duplicates()
    df.related.replace(2, 0, inplace=True)
    return(df)

def save_data(df, database_filename):
    """
    Saves messages to an SQLite database.
    
    Args:
        df (pandas dataframe): cleaned and labelled message data.
        database_filename (string): where the SQLite database will be saved.
    """
    engine = create_engine('sqlite:///{}'.format(database_filename))
    df.to_sql('LabelledMessages', engine, index=False, if_exists='replace')
    engine.dispose()

def main():
    if len(sys.argv) == 4:

        messages_filepath, categories_filepath, database_filepath = sys.argv[1:]

        print('Loading data...\n    MESSAGES: {}\n    CATEGORIES: {}'
              .format(messages_filepath, categories_filepath))
        df = load_data(messages_filepath, categories_filepath)

        print('Cleaning data...')
        df = clean_data(df)
        
        print('Saving data...\n    DATABASE: {}'.format(database_filepath))
        save_data(df, database_filepath)
        
        print('Cleaned data saved to database!')
    
    else:
        print('Please provide the filepaths of the messages and categories '\
              'datasets as the first and second argument respectively, as '\
              'well as the filepath of the database to save the cleaned data '\
              'to as the third argument. \n\nExample: python process_data.py '\
              'disaster_messages.csv disaster_categories.csv '\
              'DisasterResponse.db')


if __name__ == '__main__':
    main()
