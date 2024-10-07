import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
from matplotlib.ticker import FuncFormatter

# Set gaya untuk seaborn
sns.set(style='dark')

def get_total_count_by_hour(hour_data):
    return hour_data.groupby("hours").agg({"grand_total": "sum"})

def filter_days_by_date(day_data, start_date, end_date):
    return day_data.query(f'dateday >= "{start_date}" and dateday <= "{end_date}"')

def total_orders_by_hour(hour_data):
    return hour_data.groupby("hours").grand_total.sum().sort_values(ascending=False).reset_index()

def total_orders_by_season(day_data):
    return day_data.groupby("season").grand_total.sum().reset_index()

# Memuat data
day_data = pd.read_csv('dashboard/days_data.csv')
hour_data = pd.read_csv('dashboard/hours_data.csv')

for data in [day_data, hour_data]:
    data['dateday'] = pd.to_datetime(data['dateday'])

min_date = day_data["dateday"].min()
max_date = day_data["dateday"].max()

# Sidebar untuk memilih rentang tanggal
with st.sidebar:
    start_date, end_date = st.date_input(
        label='Rentang Waktu',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

# Menyaring DataFrame berdasarkan tanggal yang dipilih
main_data_days = filter_days_by_date(day_data, start_date, end_date)
main_data_hour = filter_days_by_date(hour_data, start_date, end_date)


# Visualisasi Dashboard
st.header('Data Sewa Sepeda')

# Menampilkan subheader untuk penyewaan sepeda berdasarkan musim
st.subheader("Penyewaan Sepeda Berdasarkan Musim:")

# Menyiapkan data untuk grafik pai
seasonal_totals = (
    day_data.groupby("season", observed=True)["grand_total"]
    .sum()
    .sort_values(ascending=False)
    .reset_index()
)

# Definisikan palet warna baru untuk kontras yang lebih baik
chart_colors = ["#FF6F61", "#6B5B95", "#88B04B", "#F7CAC9", "#92A8D1"]

# Membuat grafik pai
plt.figure(figsize=(10, 10))
plt.pie(
    seasonal_totals["grand_total"],
    labels=seasonal_totals["season"],
    autopct='%1.1f%%',  # Menampilkan persentase pada grafik pai
    startangle=140,     # Sudut awal untuk grafik pai
    colors=chart_colors,
    shadow=True         # Tambahkan bayangan untuk efek 3D
)

# Judul untuk grafik pai
plt.title("Distribusi Penyewaan Sepeda Berdasarkan Musim", fontsize=20, fontweight='bold')
plt.axis('equal')  # Rasio aspek sama memastikan grafik pai berbentuk lingkaran.

# Menampilkan grafik pai dalam Streamlit
st.pyplot(plt)

button_label = ("Penjelasan Data Penyewaan Sepeda Berdasarkan Musim")
if st.button(button_label):
  st.write(
        """
Analisis mengungkapkan bahwa musim gugur (fall) adalah waktu dengan tingkat penyewaan sepeda tertinggi. Faktor utama yang mempengaruhi hal ini kemungkinan adalah suhu yang lebih sejuk dan kondisi cuaca yang lebih nyaman, sehingga mendorong lebih banyak orang untuk beraktivitas di luar ruangan.
        """
    )

st.subheader("Data Penyewaan Sepeda Berdasarkan Jam:")

# Plot untuk penyewaan sepeda berdasarkan jam
sum_order_items_df = hour_data.groupby("hours")["grand_total"].sum().sort_values(ascending=False).reset_index()

# Membuat line chart
fig, ax = plt.subplots(figsize=(20, 10))

# Membuat lineplot untuk jumlah penyewaan sepeda dengan warna yang lebih gelap
sns.lineplot(
    x="hours",
    y="grand_total",
    data=sum_order_items_df,
    marker='o',  # Menambahkan marker untuk menyoroti titik data
    color="#555555", 
)

# Menambahkan garis vertikal dari setiap titik data ke sumbu y
for i in range(len(sum_order_items_df)):
    ax.vlines(x=sum_order_items_df["hours"][i], 
               ymin=0, 
               ymax=sum_order_items_df["grand_total"][i], 
               color='grey', 
               linestyle='dashed', 
               alpha=0.6)

# Menentukan titik peak dan low
peak_value = sum_order_items_df["grand_total"].max()
low_value = sum_order_items_df["grand_total"].min()
peak_hour = sum_order_items_df.loc[sum_order_items_df["grand_total"].idxmax(), "hours"]
low_hour = sum_order_items_df.loc[sum_order_items_df["grand_total"].idxmin(), "hours"]

# Menambahkan anotasi untuk peak
ax.annotate(
    f'Peak: {peak_value}', 
    xy=(peak_hour, peak_value), 
    xytext=(peak_hour, peak_value + 5000),  # Posisi teks
    arrowprops=dict(facecolor='green', arrowstyle='->'),
    fontsize=20,
    color='green'
)

# Mengatur label dan judul untuk plot
ax.set_ylabel("Jumlah Penyewa", fontsize=30)
ax.set_xlabel("Jam", fontsize=30)
ax.set_title("Penyewaan Sepeda Berdasarkan Jam", loc="center", fontsize=30)
ax.tick_params(axis='y', labelsize=25)
ax.tick_params(axis='x', labelsize=25)

# Menambahkan label jam dari 00.00 hingga 24.00
xticks = [i for i in range(25)]  # Membuat daftar jam dari 0 hingga 24
ax.set_xticks(xticks)  # Mengatur tick di sumbu x
ax.set_xticklabels([f'{i:02}.00' for i in xticks], rotation=45)  # Format label jam

# Memutar label sumbu x agar lebih mudah dibaca
plt.tight_layout()  # Menyesuaikan layout untuk tampilan yang rapi

# Menampilkan plot dalam Streamlit
st.pyplot(fig)

button_label = ("Penjelasan Data Penyewaan Sepeda Berdasarkan Jam")
if st.button(button_label):
  st.write(
        """
Hasil analisis menunjukkan bahwa waktu puncak penyewaan sepeda terjadi pada pukul 17.00. Hal ini diduga kuat dipengaruhi oleh kebiasaan banyak orang yang memilih untuk bersepeda setelah menyelesaikan aktivitas pekerjaan mereka, memanfaatkan waktu sore hari untuk berolahraga atau bersantai. Tren ini mencerminkan adanya peningkatan kebutuhan akan sarana transportasi rekreasi pada jam-jam setelah jam kerja. Di sisi lain, penyewaan sepeda mencapai titik terendah pada pukul 04.00 dini hari, saat sebagian besar orang masih berada dalam waktu istirahat atau tidur, sehingga aktivitas penyewaan sangat minim pada jam tersebut. Fenomena ini sejalan dengan pola umum aktivitas harian masyarakat, di mana kebutuhan akan penyewaan sepeda lebih rendah pada jam-jam malam hingga dini hari.
        """
    )
