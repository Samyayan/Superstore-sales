import streamlit as st
import pandas as pd
import seaborn as sns
import os
st.set_page_config(page_title="Superstore EDA", page_icon=":bar_chart:", layout="wide")
st.title(":bar_chart: Sample Superstore EDA")
st.markdown('<style>div.block-container{padding-top:2rem;}</style>', unsafe_allow_html=True)
import xlrd
file=st.sidebar.file_uploader("Upload you file", type=(['csv', 'txt', 'xls', 'xlsx']))
try:
    if file:
        df=pd.read_excel(file)
    import datetime
    col1, col2=st.columns((2))
    df["Order Date"]=pd.to_datetime(df["Order Date"])
    Start_date=pd.to_datetime(df["Order Date"]).min()
    End_date=pd.to_datetime(df["Order Date"]).max()
    with col1:
        date1=pd.to_datetime(st.date_input("Start date", Start_date))
    with col2:
        date2=pd.to_datetime(st.date_input("End date", End_date))
    df=df[(df["Order Date"]>=date1) & (df["Order Date"]<=date2)].copy()
    st.sidebar.header("Choose your filter:")
    #Create for region
    region=st.sidebar.multiselect("Pick your Region", df["Region"].unique())
    if not region:
        df2=df.copy()
    else:
        df2=df[df["Region"].isin(region)]
    #Create for country: country is same i.e., US
    #Create for state
    state=st.sidebar.multiselect("Pick your State", df2["State"].unique())
    if not state:
        df3=df2.copy()
    else:
        df3=df2[df2["State"].isin(state)]
    #Create for city
    city=st.sidebar.multiselect("Pick your City", df3["City"].unique())
    #Filtering of data
    if not region and not state and not city:
        filtered_df=df
    elif not state and not city:
        filtered_df=df[df["Region"].isin(region)]
    elif not region and not city:
        filtered_df=df[df["State"].isin(state)]
    elif not region and not state:
        filtered_df=df[df["City"].isin(city)]
    elif state and city:
        filtered_df=df3[df3["State"].isin(state) & df3["City"].isin(city)]
    elif state and city:
        filtered_df=df3[df3["State"].isin(state) & df3["City"].isin(city)]
    elif region and state:
        filtered_df=df3[df3["Region"].isin(region) & df3["State"].isin(state)]
    elif region and city:
        filtered_df=df3[df3["Region"].isin(region) & df3["City"].isin(city)]
    elif city:
        filtered_df=df3[df3["City"].isin(city)]
    else:
        filtered_df=df3[df3["Region"].isin(region) & df3["State"].isin(state) & df3["City"].isin(city)]
    category_df=filtered_df.groupby(by=["Category"], as_index=False)["Sales"].sum()
    import plotly.express as px
    with col1:
        st.subheader("Category wise sales")
        fig=px.bar(category_df, x="Category", y="Sales", text=['${:,.2f}'.format(x) for x in category_df["Sales"]], template="seaborn")
        st.plotly_chart(fig, use_container_width=True, height=200)
    with col2:
        st.subheader("Region wise sales")
        fig=px.pie(filtered_df, values="Sales", names="Region", hole=0.5)
        fig.update_traces(text=filtered_df["Region"], textposition="outside")
        st.plotly_chart(fig, use_container_width=True)
    #Downloading data
    cl1, cl2 =st.columns((2))
    with cl1:
        with st.expander("Category_View_Data"):
            st.write(category_df.style.background_gradient(cmap="Blues"))
            csv=category_df.to_csv(index=False)
            st.download_button("Download Data", data=csv, file_name="Category.csv", mime="text/csv",
                               help='Click here to download the data as a csv file')
        

    with cl2:
        with st.expander("Region_View_Data"):
            region=filtered_df.groupby(by="Region", as_index=False)["Sales"].sum()
            st.write(region.style.background_gradient(cmap="Oranges"))
            csv=region.to_csv(index=False)
            st.download_button("Download Data", data=csv, file_name="Region.csv", mime="text/csv",
                               help='Click here to download the data as a csv file')

    filtered_df["month_year"]=filtered_df["Order Date"].dt.to_period("M")
    st.subheader("Time-series analysis")

    #Creating line-chart
    linechart=pd.DataFrame(filtered_df.groupby(filtered_df["month_year"].dt.strftime("%Y:%b"))["Sales"].sum()).reset_index()
    fig2=px.line(linechart, x="month_year", y="Sales", labels={"Sales":"Amount"}, height=500, width=1000, template='gridon')
    st.plotly_chart(fig2, use_container_width=True)
    #Downloading line-chart data
    with st.expander("Time-series_View_Data"):
            st.write(linechart.T.style.background_gradient(cmap="Oranges"))
            csv=linechart.to_csv(index=False)
            st.download_button("Download Data", data=csv, file_name="Region.csv", mime="text/csv")
    #Creating TreeMap
    st.subheader("Hierarchical view of Sales using TreeMap")
    fig3=px.treemap(filtered_df, path=["Region", "Category", "Sub-Category"], values="Sales", hover_data=["Sales"], color="Sub-Category")
    fig3.update_layout(width=800, height=650)
    st.plotly_chart(fig3, use_container_width=True)

    chart1, chart2=st.columns((2))
    with chart1:
        st.subheader("Segement wise Sales")
        fig=px.pie(filtered_df, values="Sales", names="Segment", template="plotly_dark")
        fig.update_traces(text=filtered_df["Segment"], textposition="inside")
        st.plotly_chart(fig, use_container_width=True)
    with chart2:
        st.subheader("Category wise Sales")
        fig=px.pie(filtered_df, values="Sales", names="Category", template="gridon")
        fig.update_traces(text=filtered_df["Category"], textposition="inside")
        st.plotly_chart(fig, use_container_width=True)

    import plotly.figure_factory as ff
    st.subheader(":point_right: Month wise sub-category sales summary")
    with st.expander("Summary_Table"):
        df_sample=df[0:5][["Region", "State", "City","Category", "Sales", "Profit", "Quantity"]]
        fig=ff.create_table(df_sample, colorscale="Cividis")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("Month wise sub-category table")
    filtered_df["month"]=filtered_df["Order Date"].dt.month_name()
    sub_category_year=pd.pivot_table(data=filtered_df, values="Sales", index=["Sub-Category"], columns='month')
    st.write(sub_category_year.style.background_gradient(cmap="Blues"))

    #Scatter plot
    data1=px.scatter(filtered_df, x="Sales", y="Profit", size="Quantity")
    data1["layout"].update(title="Relation betwween sales and profits using scatter plot.",
                            xaxis=dict(title="Sales", ),
                           yaxis=dict(title="Profit"))
    st.plotly_chart(data1, use_container_width=True)

    with st.expander("View Data"):
        st.write(filtered_df.iloc[:500, 1:20:2].style.background_gradient(cmap="Oranges"))
    #Download data
    csv=df.to_csv(index=False)
    st.download_button("Download data", data=csv, file_name="Data.csv", mime="text/csv")
except:
    st.title ("Please Upload superstore sales data")
