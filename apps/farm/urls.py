from django.urls import path
from django.contrib.auth.decorators import login_required
from .views import *

urlpatterns = [
    path('product/', login_required(get_product_list), name='product'),
    path('modal_product_create/', login_required(modal_product_create), name='modal_product_create'),
    path('create_product/', login_required(create_product), name='create_product'),
    path('modal_product_update/', login_required(modal_product_update), name='modal_product_update'),
    path('update_product/', login_required(update_product), name='update_product'),
    path('inventory_transaction/', login_required(get_inventory_transaction_list), name='inventory_transaction'),
    path('inventory_transaction_grid/', login_required(get_inventory_transaction_grid), name='inventory_transaction_grid'),
    path('modal_product_selection/', login_required(modal_product_selection), name='modal_product_selection'),
    path('modal_inventory_entry_create/', login_required(modal_inventory_entry_create), name='modal_inventory_entry_create'),
    path('modal_inventory_exit_create/', login_required(modal_inventory_exit_create), name='modal_inventory_exit_create'),
    path('create_inventory_entry/', login_required(create_inventory_entry), name='create_inventory_entry'),
    path('create_inventory_exit/', login_required(create_inventory_exit), name='create_inventory_exit'),
    path('modal_inventory_transaction_update/', login_required(modal_inventory_transaction_update), name='modal_inventory_transaction_update'),
    path('update_inventory_transaction/', login_required(update_inventory_transaction), name='update_inventory_transaction'),
    
    # Crop Type URLs
    path('crop_type/', login_required(get_crop_type_list), name='crop_type'),
    path('modal_crop_type_create/', login_required(modal_crop_type_create), name='modal_crop_type_create'),
    path('create_crop_type/', login_required(create_crop_type), name='create_crop_type'),
    path('modal_crop_type_update/', login_required(modal_crop_type_update), name='modal_crop_type_update'),
    path('update_crop_type/', login_required(update_crop_type), name='update_crop_type'),
    
    # Plot URLs
    path('plot/', login_required(get_plot_list), name='plot'),
    path('modal_plot_create/', login_required(modal_plot_create), name='modal_plot_create'),
    path('create_plot/', login_required(create_plot), name='create_plot'),
    path('modal_plot_update/', login_required(modal_plot_update), name='modal_plot_update'),
    path('update_plot/', login_required(update_plot), name='update_plot'),
    
    # Crop URLs
    path('crop/', login_required(get_crop_list), name='crop'),
    path('modal_crop_create/', login_required(modal_crop_create), name='modal_crop_create'),
    path('create_crop/', login_required(create_crop), name='create_crop'),
    path('modal_crop_update/', login_required(modal_crop_update), name='modal_crop_update'),
    path('update_crop/', login_required(update_crop), name='update_crop'),
    
    # Crop Cycle Cost URLs
    path('crop_cycle_cost/', login_required(get_crop_cycle_cost_list), name='crop_cycle_cost'),
    path('crop_cycle_cost_grid/', login_required(get_crop_cycle_cost_grid), name='crop_cycle_cost_grid'),
    path('modal_crop_cycle_cost_create/', login_required(modal_crop_cycle_cost_create), name='modal_crop_cycle_cost_create'),
    path('create_crop_cycle_cost/', login_required(create_crop_cycle_cost), name='create_crop_cycle_cost'),
    path('modal_crop_cycle_cost_update/', login_required(modal_crop_cycle_cost_update), name='modal_crop_cycle_cost_update'),
    path('update_crop_cycle_cost/', login_required(update_crop_cycle_cost), name='update_crop_cycle_cost'),
    
    # Service Type URLs
    path('modal_service_type_create/', login_required(modal_service_type_create), name='modal_service_type_create'),
    path('create_service_type/', login_required(create_service_type), name='create_service_type'),
    path('modal_service_type_update/', login_required(modal_service_type_update), name='modal_service_type_update'),
    path('update_service_type/', login_required(update_service_type), name='update_service_type'),
    path('get_service_types/', login_required(get_service_types), name='get_service_types'),
]
