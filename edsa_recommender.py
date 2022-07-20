"""

    Streamlit webserver-based Recommender Engine.

    Author: Explore Data Science Academy.

    Note:
    ---------------------------------------------------------------------
    Please follow the instructions provided within the README.md file
    located within the root of this repository for guidance on how to use
    this script correctly.

    NB: !! Do not remove/modify the code delimited by dashes !!

    This application is intended to be partly marked in an automated manner.
    Altering delimited code may result in a mark of 0.
    ---------------------------------------------------------------------

    Description: This file is used to launch a minimal streamlit web
	application. You are expected to extend certain aspects of this script
    and its dependencies as part of your predict project.

	For further help with the Streamlit framework, see:

	https://docs.streamlit.io/en/latest/

"""
# Streamlit dependencies
import email
from turtle import onclick, window_width
from requests import options
import streamlit as st

# Data handling dependencies
import pandas as pd
import numpy as np


#from sympy import im

# Custom Libraries
from utils.data_loader import load_movie_titles
from recommenders.collaborative_based import collab_model
from recommenders.content_based import content_model

#various functions 
from eda.mymodules import *

import matplotlib.pyplot as plt
import seaborn as sns

#import re


# Data Loading
title_list = load_movie_titles('resources/data/movies.csv')




# App declaration
def main():

    # DO NOT REMOVE the 'Recommender System' option below, however,
    # you are welcome to add more options to enrich your app.
    page_options = ["Recommender System","EDA","Solution Overview","Feedback",'Documentation','About']

    # -------------------------------------------------------------------
    # ----------- !! THIS CODE MUST NOT BE ALTERED !! -------------------
    # -------------------------------------------------------------------
    st.sidebar.image('resources\imgs\Screen_lot.jpg',use_column_width=True)
    page_selection = st.sidebar.selectbox("Choose Option", page_options)
    if page_selection == "Recommender System":
        # Header contents
        st.write('# Movie Recommender Engine')
        st.write('### EXPLORE Data Science Academy Unsupervised Predict')
        st.image('resources/imgs/Image_header.png',use_column_width=True)
        # Recommender System algorithm selection
        sys = st.radio("Select an algorithm",
                       ('Content Based Filtering',
                        'Collaborative Based Filtering'))

        # User-based preferences
        st.write('### Enter Your Three Favorite Movies')
        movie_1 = st.selectbox('Fisrt Option',title_list[14930:15200])
        movie_2 = st.selectbox('Second Option',title_list[25055:25255])
        movie_3 = st.selectbox('Third Option',title_list[21100:21200])
        fav_movies = [movie_1,movie_2,movie_3]

        # Perform top-10 movie recommendation generation
        if sys == 'Content Based Filtering':
            if st.button("Recommend"):
                try:
                    with st.spinner('Crunching the numbers...'):
                        top_recommendations = content_model(movie_list=fav_movies,
                                                            top_n=10)
                    st.title("We think you'll like:")
                    for i,j in enumerate(top_recommendations):
                        st.subheader(str(i+1)+'. '+j)
                except:
                    st.error("Oops! Looks like this algorithm does't work.\
                              We'll need to fix it!")


        if sys == 'Collaborative Based Filtering':
            if st.button("Recommend"):
                try:
                    with st.spinner('Crunching the numbers...'):
                        top_recommendations = collab_model(movie_list=fav_movies,
                                                           top_n=10)
                    st.title("We think you'll like:")
                    for i,j in enumerate(top_recommendations):
                        st.subheader(str(i+1)+'. '+j)
                except:
                    st.error("Oops! Looks like this algorithm does't work.\
                              We'll need to fix it!")


    # -------------------------------------------------------------------

    # ------------- SAFE FOR ALTERING/EXTENSION -------------------

    if page_selection == "EDA":
        train_df = pd.read_csv('resources/data/train.csv')
        eda_df = train_df[train_df['userId']!=72315]
        mov_df = pd.read_csv('resources\data\movies.csv')
        rate_df = pd.read_csv('resources\\data\\ratings.csv')
        
        #movie and rating dataframe 
        
        movie_rating_df = pd.merge(left=mov_df,right=rate_df,how='inner',left_on='movieId',right_on='movieId')
        movie_rating_df.drop(['movieId','timestamp','userId'],axis=1,inplace=True)
        #delete dataframes to save memory
        
        del rate_df

        gp_mov = movie_rating_df.groupby(by=['title','genres']).mean()
        
        gp_mov.reset_index(inplace=True)
        pattern = '\((\d{4})\)'
        gp_mov['year'] = gp_mov.title.str.extract(pattern,expand=False).fillna(2016).astype('int64')

        #Showing dataframe
        st.subheader('Movie Dataset')

        if st.checkbox('Filter Dataset'):

            message = 'Move sliders to filter dataframe'
            year_slide = ''
            slider_1, slider_2 = st.slider('%s' % (message),0,len(gp_mov)-1,[0,len(gp_mov)-1],1)
            yslider_1,y_slider_2 = st.slider('%s' % (message),1900,2020,(1902,2016))
            
            st.success('Starts from {} to {} '.format(slider_1,slider_2))
            
            st.dataframe(gp_mov.loc[slider_1:slider_2])
            st.write(download_csv('Filtered Data Frame',gp_mov.iloc[:][slider_1:slider_2]),unsafe_allow_html=True)
            
            

        #Searching movie  with Details
        if st.checkbox('Show movie details'):
            movie_title = gp_mov.title.unique()
            movie_sel = st.selectbox('Select a Movie',movie_title)
            
            if (movie_sel in movie_title):
                selected_movie = gp_mov[gp_mov.title == movie_sel]
                df_columns = {'Title':[movie_sel],
                                'Year': selected_movie.year,
                                'Genre':[selected_movie.genres.unique()[0]],
                                'Highest Rating':[round(selected_movie.rating.max(),1)],
                                'Lowest Ratings':[round(selected_movie.rating.min(),1)],
                                'Average Rating':[round(selected_movie.rating.mean(),1)],
                                'User Review':[selected_movie.shape[0]]}

                st.dataframe(df_columns)    
                st.success('{} has been rated {} time(s) with an average IMDB rating  of {}'.format(movie_sel,selected_movie.shape[0],round(selected_movie.rating.mean(),2)))

            else:
                st.warning('Movie not present in database')
        
        #Movies by Genre
        if st.checkbox('Show movies by Genre'):
            
            genres = genre_extractor(movie_rating_df,'genres')
            genres_sel = st.selectbox('Search movies by Genre',genres[1:])

            if genres_sel in genres:
                gp_mov['genres_clean'] = gp_mov.genres.apply(lambda x: ' '.join(x.split('|')))
                gp_mov['genreclass'] = gp_mov.genres_clean.str.find(genres_sel)
                st.dataframe(gp_mov[gp_mov.genreclass >=0][['title','genres','rating','year']])
                gp_mov.drop(['genres_clean','genreclass'],inplace=True,axis=1)

        
        # Displaying charts
        
            
        ratings_selected = st.selectbox('Select a type of rating',['Count Plot','Distplot','Mean Plot','Plot Rating'])
        if ratings_selected == 'Count Plot':

            user_count = st.number_input('Insert a number',min_value=3,max_value=20,value=8,step=1,key='user_count')
            user_ratings_count(eda_df,int(user_count))
            
        elif ratings_selected == 'Distplot':
            ratings_distplot(eda_df)

        elif ratings_selected == 'Mean Plot':
            color_pic = st.color_picker('Pick a color','#4D17A0')
            mean_ratings_scatter(eda_df,color=color_pic)
            #st.write(user_ratings_count(train_df,8))
        elif ratings_selected == 'Plot Rating':
            plot_ratings(eda_df,mov_df, 10000, 15, '#4D17A0', True, 'mean')

        





    if page_selection == "Solution Overview":
        st.title("The Screen lot Project")
        st.write("Describe your winning approach on this page")
        st.markdown('''Having been given a sourced and clean data set, (the MovieLens dataset) which has been pre-enriched with additional data, and resampled for fair evaluation purposes, We have a task to use this raw data to build a Recommendation system algorithm (Screen lot) based on content or collaborative filtering, capable of accurately predicting how a user will rate a movie they have not yet viewed, based on their historical preferences. The idea of this algorithm is to predict the movies that would be enjoyed by a viewer based on their reactions to the movies that they have already watched. For more information on how Screenlot works and the technical details of the App, please check out the [documentation] page.''')
        


    # You may want to add more sections here for aspects such as an EDA,
    # or to provide your business pitch.



    if page_selection == "Feedback":
        
        #st.session_state;
        with st.container():
            
            name = st.text_input('Name')
            mail = st.text_input('Email')
            phone = st.text_input('Phone Number')
            
            #radio buttons
            feed_radio = st.radio('Select an option',('Feedback','Contact Us','Other'),key='radio_option')         
            
            if feed_radio == 'Other':
                subject = st.text_input('Subject') 
            
            message = st.text_area('Message')
            
            if st.button('Submit'):
                if feed_radio != "Other":
                    st.success('Your {} form has been logged'.format(feed_radio))

                else:
                    st.success('Your comment has been logged'.format(feed_radio))


    if page_selection == "Documentation":
       
        st.title('Documentation')
        
        st.header("Overview")
        st.write("In order to maximize profit and  guarantee a personalized experience for customers, we have built a movie recommendation app that iterates through a viewer's previous viewing preferences and movie viewer ratings and uses the information contained therein to predict what unseen movie the viewer is likely to enjoy. most online content providers rely on recommendation systems such as this to maximally exploit the long tail. The long tail is a business strategy that allows companies to realize significant profits by selling low volumes of hard-to-find items to many customers, instead of only selling large volumes of a reduced number of popular items (For more on long tail, please click [*here*](https://medium.com/@kyasar.mail/recommender-systems-what-long-tail-tells-91680f10a5b2)).")
        st.image('https://media.wired.com/photos/5a5957cf2bbf59566d73366b/master/w_1600%2Cc_limit/FF_170_tail6_f.gif',caption='Long Tail')
        st.write("Our recommendation system allows the client to achieve this by actively recommending products based on the app's built-in algorithm rather than relying on the customers to scan through potentially millions of options in order to find these products themselves. A broad base of consumer sentiment, spanning multiple demographic and geographic categories is used as input to train the algorithm, hence increasing the accuracy of the app, and providing sound insights that convert into sound matches as regards movies that unique viewers are likely to enjoy. ")
        
        
        st.subheader('Featured  Recommendation Engines')
        st.write("Of the three main types of recommendation engines that exist, Our app features two main recommendation engines as detailed below.")

        st.subheader("Collaborative filtering")  
        st.write("Collaborative filtering focuses on collecting and analyzing data on user behavior, activities, and preferences, to predict what a person will like, based on their similarity to other users. To plot and calculate these similarities, collaborative filtering uses a matrix-style formula. An advantage of collaborative filtering is that it doesn’t need to analyze or understand the content (products, films, books). It simply picks items to recommend based on what they know about the user.")

        st.subheader("Content-based filtering")
        st.write("Content-based filtering works on the principle that if you like a particular item, you will also like this other item. To make recommendations, algorithms use a profile of the customer’s preferences and a description of an item (genre, product type, color, word length etc) to work out the similarity of items using cosine and Euclidean distances. The downside of content-based filtering is that the system is limited to recommending products or content similar to what the person is already buying or using. It can’t go beyond this to recommend other types of products or content. For example, it couldn’t recommend products beyond")

        st.subheader("Data Details")
        st.write("This dataset consists of several million 5-star ratings obtained from users of the online [MovieLens](http://movielens.org/) movie recommendation service. The MovieLens dataset has long been used by the industry. For this project, we'll be using a special version of the MovieLens dataset which has been enriched with additional data and resampled for fair evaluation purposes. The data for the MovieLens dataset is maintained by the [GroupLens](http://grouplens.org/) research group in the Department of Computer Science and Engineering at the University of Minnesota. Additional movie content data was legally scraped from [IMDB](https://www.imdb.com/).")

        st.subheader("Model performance")
        st.write("The evaluation metric for this competition is [Root Mean Square Error](https://surprise.readthedocs.io/en/stable/accuracy.html). Root Mean Square Error (RMSE) is commonly used in regression analysis and forecasting and measures the standard deviation of the residuals arising between predicted and actual observed values for a modeling process. For our task of generating user movie ratings via recommendation algorithms, the formula is given by:")
        st.image("resources/imgs/rsme.jpg",caption="Root Mean Squared Error")
        st.write('''Where R is the total number of recommendations generated for users and movies, with $r_{ui} $ and $\hat{r_{ui}}$ being the true, and predicted ratings for user ***u*** watching movie ***i***, respectively.''')
        
        
    if page_selection == "About":    
        #st.subheader("Team NM 2")
        st.markdown("<h3 style='text-align: center; color: magenta; background: cyan; margin: 3px'>TEAM NM2</h1>", unsafe_allow_html=True)
        st.write("Team NM-2  is a team at the explore DS academy, 2022 Data science cohort and we employ our training here at explore DS to extract valuable insights from all kinds of raw data. Data collection and analysis are increasingly becoming very useful in industries and economies worldwide. With advances in science and technology (particularly information technology), we are in an age where an astounding quantity of data in many different forms is generated every second. This data usually has hidden insights on trends, habits, developments, changes, etc that may not be immediately identified, but are very valuable to companies and other entities for the purpose of making informed decisions.")
        st.write("Before now, it was near impossible to process these large swaths of data in order to reveal these insights. With the developments in the field of data science and through the expertise which we seek to express, we will show how data can be processed to not only reveal the insight hidden in them but also to present the discoveries made in the process in a form that is digestible by non-technical audiences. Our team is made up of 5  professionals who excel in the fields of Business Management, marketing and promotions, technical data science, IT communications, and Administration. Please refer below for  the full profiles of all team members.")
		#st.write('Before now, it was near impossible to process these large swaths of data in order to reveal these insights. With the developments in the field of data science and through the expertise which we seek to express, we will show how data can be processed to not only reveal the insight hidden in them but also to present the discoveries made in the process in a form that is digestible by non-technical audiences. Our team is made up of 5  professionals who excel in the fields of Business Management, marketing and promotions, technical data science, IT communications, and Administration. Please refer to this link to access the full profiles of all team members.')

        from PIL import Image
        prince,huzaifa = st.columns(2)
    
        dan,jerry,izu =  st.columns(3)

        dan_img = Image.open('resources\imgs\Daniel.png')
        jerry_img = Image.open('resources\imgs\Jerry.png')
        huzaifa_img = Image.open('resources\imgs\huzaius.png')
        prince_img = Image.open('resources\imgs\Prince.png')
        izu_img = Image.open('resources\imgs\izunna.png')

        with prince:
            st.image(prince_img,caption='Prince Okon- Team lead')
            with st.expander("View Profile"):
                st.write('Profile')
        
        with huzaifa:
            st.image(huzaifa_img,caption='Huzaifa Abu - Technical Lead')
            with st.expander("View Profile"):
                st.write('Profile')

        with dan:
            st.image(dan_img,caption='Odukoya Daniel - Administrator')
            with st.expander("View Profile"):
                st.write('Profile')

        with jerry:
            st.image(jerry_img,caption='Jerry Iriri - Chief Designer')
            with st.expander("View Profile"):
                st.write('Profile')

        with izu:
            st.image(izu_img,caption='Izunna Eneude - Quality Control')
            with st.expander("View Profile"):
                st.write('Profile')
              

            

            
            

                


if __name__ == '__main__':
    
    main()
