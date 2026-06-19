from statsmodels.stats.proportion import proportions_ztest
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
pd.set_option('display.max_columns', None)

# ----Data----
website_pageviews = pd.read_csv('website_pageviews.csv')
website_sessions = pd.read_csv('website_sessions.csv')
# -------------------

# 1.
test = pd.merge(website_pageviews, website_sessions, how='left',
                on='website_session_id', suffixes=('_page', '_session'))

test['created_at_page'] = pd.to_datetime(test['created_at_page'])
test['year'] = test['created_at_page'].dt.year
test['month'] = test['created_at_page'].dt.month

test = test.sort_values(['website_session_id', 'created_at_page'])
landing_pages = test.groupby('website_session_id', as_index=False).agg(
    landers=('pageview_url', 'first'))
test = test.merge(landing_pages[[
                  'website_session_id', 'landers']], on='website_session_id', how='left')
ab_test = test[test['landers'].isin(['/lander-1', '/lander-2', '/lander-3'])]


ab_test_final = ab_test.groupby(['landers', 'pageview_url'], as_index=False).agg(
    pageview=('pageview_url', 'size'))

ab_final = ab_test_final.pivot(
    columns='pageview_url', index='landers', values='pageview').fillna(0)


ab_final['lander'] = ab_final['/lander-1'] + \
    ab_final['/lander-2'] + ab_final['/lander-3']
ab_final['billing'] = ab_final['/billing'] + ab_final['/billing-2']
result = ab_final[['lander', '/products', '/cart',
                   '/shipping', 'billing', '/thank-you-for-your-order']]

# res = result.to_excel('result.xlsx')

# Перевірка на статистично значущу різницю між конверсіями різних лендінгів
result = result.copy()
result['convertion'] = result['/thank-you-for-your-order'] / \
    result['lander'] * 100

success = [
    result.loc['/lander-1', '/thank-you-for-your-order'],
    result.loc['/lander-2', '/thank-you-for-your-order']
]

nobs = [
    result.loc['/lander-1', 'lander'],
    result.loc['/lander-2', 'lander']
]

z_stat, p_value = proportions_ztest(success, nobs)

print(f'Z-statistic: {z_stat:.4f}')
print(f'P-value: {p_value:.10f}')
# Було проведено z-тест для порівняння конверсій лендінгів /lander-1 та
# /lander-2. Конверсія /lander-1 становила 4.53%, тоді як конверсія
# /lander-2 — 7.72%. Отримане значення статистики Z = -23.54,
# p-value < 0.001. Отже, різниця між конверсіями є статистично значущою,
# а лендінг /lander-2 демонструє суттєво кращу ефективність.
