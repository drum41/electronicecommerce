import streamlit as st
import plotly.express as px
import pandas as pd
import warnings
from plotly.subplots import make_subplots
import plotly.graph_objects as go

warnings.filterwarnings('ignore')


st.set_page_config(page_title="Electronic ecommerce store", page_icon=":bar_chart:", layout="wide")

st.title(":bar_chart: Electronic ecommerce store")
st.markdown('<style>div.block-container{padding-top:1rem;}</style>',unsafe_allow_html=True)

fl = st.file_uploader(":file_folder: Upload a file",type=(["csv","txt","xlsx","xls"]))
if fl is not None:
    filename = fl.name
    st.write(filename)
    df = pd.read_csv(filename, encoding = "ISO-8859-1")
else:
    df = pd.read_csv("final_data.csv", encoding = "ISO-8859-1")


######### ------------------------------------ FILTER ----------------------------------------------------- #########
df = pd.DataFrame(df)
df['event_time'] = pd.to_datetime(df['event_time'])
# Filter data for year 2020 and remove potential incorrect timestamps
df = df[(df['event_time'].dt.year == 2020) & (df['event_time'] != '1970-01-01')]



col1, col2 = st.columns((2))
df["event_time"] = pd.to_datetime(df["event_time"])

# Getting the min and max date 
startDate = pd.to_datetime(df["event_time"]).min()
endDate = pd.to_datetime(df["event_time"]).max()

with col1:
    date1 = pd.to_datetime(st.date_input("Start Date", startDate))

with col2:
    date2 = pd.to_datetime(st.date_input("End Date", endDate))

df = df[(df["event_time"] >= date1) & (df["event_time"] <= date2)].copy()


st.sidebar.header("Choose your filter: ")
# Create for Category
Category = st.sidebar.multiselect("Choose Category", df["Category"].unique())
if not Category:
    df2 = df.copy()
else:
    df2 = df[df["Category"].isin(Category)]

# Create for Product category
Product = st.sidebar.multiselect("Choose Product", df2["Product category"].unique())
if not Product:
    df3 = df2.copy()
else:
    df3 = df2[df2["Product category"].isin(Product)]

# Create for brand
brand = st.sidebar.multiselect("Pick the brand",df3["brand"].unique())

# Filter the data based on Category, Product category and brand

if not Category and not Product and not brand:
    filtered_df = df
elif not Product and not brand:
    filtered_df = df[df["Category"].isin(Category)]
elif not Category and not brand:
    filtered_df = df[df["Product category"].isin(Product)]
elif Product and brand:
    filtered_df = df3[df["Product category"].isin(Product) & df3["brand"].isin(brand)]
elif Category and brand:
    filtered_df = df3[df["Category"].isin(Category) & df3["brand"].isin(brand)]
elif Category and Product:
    filtered_df = df3[df["Category"].isin(Category) & df3["Product category"].isin(Product)]
elif brand:
    filtered_df = df3[df3["brand"].isin(brand)]
else:
    filtered_df = df3[df3["Category"].isin(Category) & df3["Product category"].isin(Product) & df3["brand"].isin(brand)]

######### ------------------------------------ FILTER ----------------------------------------------------- #########
total_revenue=float(filtered_df['price'].sum())
total_number_sales = filtered_df['order_id'].count()
aov = total_revenue/total_number_sales
total_order = total_number_sales / filtered_df['order_id'].nunique()

total1, total2, total3, total4 = st.columns(4,gap="large")
with total1:
    st.info("Total Revenue", icon="💸")
    st.metric(label="Sum USD", value=f"{total_revenue:,.0f}")
with total2:
    st.info("Total Number of Sales", icon="📊")
    st.metric(label="Sum", value=f"{total_number_sales:,.0f}")
with total3:
    st.info("Average Order Value", icon="💸")
    st.metric(label="Sum USD", value=f"{aov:.1f}")
with total4:
    st.info("Average Items/ Order", icon="📦")
    st.metric(label="Item", value=f"{total_order:.1f}")

st.markdown("---")

######### -------------------------------- chart -------------------------------------------- #########


####################  Time Series Chart
df_ts = filtered_df.groupby(df['event_time'].dt.date)['price'].sum().reset_index()
fig_ts = px.area(df_ts, x='event_time', y='price', title='Total Sales Over Time')

# Calculate the total sales by category
df_category = filtered_df.groupby('Category')['price'].sum().reset_index()
df_category = df_category.sort_values(by='price', ascending=False)

# Calculate the number of sales by category
df_category_prod_count = filtered_df.groupby('Category')['order_id'].count().reset_index()
df_category_prod_count = df_category_prod_count.set_index('Category').loc[df_category['Category']].reset_index()

# Calculate the AOV by category
df_category_aov = filtered_df.groupby('Category')['price'].mean().reset_index()
df_category_aov = df_category_aov.set_index('Category').loc[df_category['Category']].reset_index()

# Combine the two charts into a single figure with secondary y-axis enabled
fig_category_combo = make_subplots(specs=[[{"secondary_y": True}]])

# Add bar chart for the primary y-axis
fig_category_combo.add_trace(
    go.Bar(x=df_category['Category'], y=df_category['price'], name='Sales', text=df_category['price']),
    secondary_y=False,
)

# Add line chart for the secondary y-axis (Number of Sales)
fig_category_combo.add_trace(
    go.Scatter(
        x=df_category['Category'],
        y=df_category_prod_count['order_id'],
        name='Number of Sales',
        mode='lines+markers'
    ),
    secondary_y=True,
)

# Add line chart for the secondary y-axis (AOV)
fig_category_combo.add_trace(
    go.Scatter(
        x=df_category_aov['Category'],
        y=df_category_aov['price'],
        name='AOV',
        mode='lines+markers',
        yaxis='y2'  # Ensure this is linked to the secondary y-axis
    ),
    secondary_y=True,
)

# Update layout to include both y-axes and titles
fig_category_combo.update_layout(
    title='Sales Distribution by Category with Line Chart of Number of Sales and AOV',
    xaxis_title='Category',
    yaxis_title='Sales ($)',
    yaxis2_title='Number of Sales & AOV',
)

# Set y-axis to start from zero
fig_category_combo.update_yaxes(title_text="Sales ($)", secondary_y=False, showgrid=False, range=[0, max(df_category['price'])])

# Update secondary y-axis range if necessary to include both Number of Sales and AOV
# You might need to adjust this manually to get a meaningful chart
max_number_of_sales = max(df_category_prod_count['order_id'])
max_aov = max(df_category_aov['price'])
max_secondary_axis = max(max_number_of_sales, max_aov)

fig_category_combo.update_yaxes(title_text="Number of Sales & AOV", secondary_y=True, showgrid=False, range=[0, max_secondary_axis])

# Update the hover template for the line chart
fig_category_combo['data'][1].update(hovertemplate='Number of Sales: %{y}')
fig_category_combo['data'][2].update(hovertemplate='AOV: %{y}')


st.plotly_chart(fig_ts,use_container_width=True)
st.plotly_chart(fig_category_combo,use_container_width=True)


################### Brand Sales Chart


# Group by brand and calculate total sales
df_brand = filtered_df.groupby('brand')['price'].sum().reset_index()
# Sort brands by sales in descending order
df_brand_sorted = df_brand.sort_values(by='price', ascending=False)
# Select top 10 brands
top_10_brands = df_brand_sorted.head(10)
# Calculate total sales of all brands
total_sales_all_brands = filtered_df['price'].sum()
# Group by brand and calculate total sales
df_brand = filtered_df.groupby('brand')['price'].sum().reset_index()
# Sort brands by sales in descending order
df_brand_sorted = df_brand.sort_values(by='price', ascending=False)
# Calculate total sales of top 10 brands
total_sales_top_10 = top_10_brands['price'].sum()
# Create a DataFrame for "Others" category
others_sales = total_sales_all_brands - total_sales_top_10
df_others = pd.DataFrame({'brand': ['Others'], 'price': [others_sales]})
# Concatenate top 10 brands and "Others" DataFrame
df_combined = pd.concat([top_10_brands, df_others])

# Number of product sales
df_product = filtered_df.groupby('Product category')['price'].sum().reset_index()
df_product_sorted = df_product.sort_values(by='price', ascending=False)
# Select top 10 brands
top_10_product = df_product_sorted.head(10)
# Calculate total sales of top 10 brands
total_sales_top_10 = top_10_product['price'].sum()
top_10_product = top_10_product.sort_values(by='price', ascending=False)


col1, col2 = st.columns((2))
with col1:
    st.subheader("Brand performance")
    fig_brand1 = px.pie(df_combined, values='price', names='brand', title='Sales Share by Brand')
    #fig_brand1.data[0].textinfo = 'label+text'
    st.plotly_chart(fig_brand1,use_container_width=True, height=200)

with col2:
    st.subheader("Top 10 Product Sales")
    fig_product = px.bar(top_10_product, x = "price", y = "Product category", text="price", orientation='h')
    st.plotly_chart(fig_product,use_container_width=True, height=200)

############download
    
# category_df = filtered_df.groupby(by = ["Category"], as_index = False)["price"].sum()
# cl1, cl2 = st.columns((2))
# with cl1:
#     with st.expander("Category_ViewData"):
#         st.write(category_df.style.background_gradient(cmap="Blues"))
#         csv = category_df.to_csv(index = False).encode('utf-8')
#         st.download_button("Download Data", data = csv, file_name = "Category.csv", mime = "text/csv",
#                             help = 'Click here to download the data as a CSV file')

# with cl2:
#     with st.expander("Region_ViewData"):
#         region = filtered_df.groupby(by = "Region", as_index = False)["Sales"].sum()
#         st.write(region.style.background_gradient(cmap="Oranges"))
#         csv = region.to_csv(index = False).encode('utf-8')
#         st.download_button("Download Data", data = csv, file_name = "Region.csv", mime = "text/csv",
#                         help = 'Click here to download the data as a CSV file')

########## Tree map 
        
st.subheader("Hierarchical view of Sales: Category, Product and Brand")
df_nnull = filtered_df.dropna(subset=["Category", "Product category", "brand"])
fig3 = px.treemap(df_nnull, path = ["Category","Product category","brand"], values = "price",hover_data = ["price"],
                  color = "Product category", color_continuous_scale = "RdBu", labels={"price":"Sales"})
fig3.data[0].textinfo = 'label+text+value'
fig3.update_layout(width = 800, height = 650)
st.plotly_chart(fig3, use_container_width=True)

# chart1, chart2 = st.columns((2))
# with chart1:
#     st.subheader('Segment wise Sales')
#     fig = px.pie(filtered_df, values = "Sales", names = "Segment", template = "plotly_dark")
#     fig.update_traces(text = filtered_df["Segment"], textposition = "inside")
#     st.plotly_chart(fig,use_container_width=True)

# with chart2:
#     st.subheader('Category wise Sales')
#     fig = px.pie(filtered_df, values = "Sales", names = "Category", template = "gridon")
#     fig.update_traces(text = filtered_df["Category"], textposition = "inside")
#     st.plotly_chart(fig,use_container_width=True)

# import plotly.figure_factory as ff
# st.subheader(":point_right: Month wise Sub-Category Sales Summary")
# with st.expander("Summary_Table"):
#     df_sample = df[0:5][["Region","State","City","Category","Sales","Profit","Quantity"]]
#     fig = ff.create_table(df_sample, colorscale = "Cividis")
#     st.plotly_chart(fig, use_container_width=True)

#     st.markdown("Month wise sub-Category Table")
#     filtered_df["month"] = filtered_df["Order Date"].dt.month_name()
#     sub_category_Year = pd.pivot_table(data = filtered_df, values = "Sales", index = ["Sub-Category"],columns = "month")
#     st.write(sub_category_Year.style.background_gradient(cmap="Blues"))



######### -------------------------------- chart -------------------------------------------- #########

# 'event_time'
# 'order_id'
# 'product_id'
# 'category_id'
# 'category_code'
# 'brand'
# 'price'
# 'user_id'
# 'Category'
# 'Sub category'
# 'Product category'
