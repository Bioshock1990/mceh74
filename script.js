const body = document.body;
const header = document.querySelector('.header');
const nav = document.querySelector('.nav');
const burger = document.querySelector('.burger');
const toTop = document.querySelector('.to-top');
const sofaModal = document.querySelector('#sofa-modal');
const requestModal = document.querySelector('#request-modal');
const galleryImage = document.querySelector('.gallery__image');
const galleryDots = document.querySelector('.gallery__dots');
const modalTitle = document.querySelector('.modal__title');
const modalPrice = document.querySelector('.modal__price');
const modalDescription = document.querySelector('.modal__description');
const modalFeatures = document.querySelector('.modal__features');
const catalogGrid = document.querySelector('#catalog-grid');

const galleryState = {
  images: [],
  index: 0,
};

const imageCache = new Map();

const lockScroll = (lock) => {
  body.style.overflow = lock ? 'hidden' : '';
};

const openModal = (modal) => {
  modal.classList.add('is-open');
  modal.setAttribute('aria-hidden', 'false');
  lockScroll(true);
};

const closeModal = (modal) => {
  if (!modal) return;
  modal.classList.remove('is-open');
  modal.setAttribute('aria-hidden', 'true');
  lockScroll(false);
};

const updateGallery = () => {
  if (!galleryState.images.length) return;
  galleryImage.style.backgroundImage = `url('${galleryState.images[galleryState.index]}')`;
  galleryDots.querySelectorAll('button').forEach((dot, index) => {
    dot.classList.toggle('active', index === galleryState.index);
  });
};

const buildDots = () => {
  galleryDots.innerHTML = '';
  galleryState.images.forEach((_, index) => {
    const dot = document.createElement('button');
    dot.addEventListener('click', () => {
      galleryState.index = index;
      updateGallery();
    });
    galleryDots.append(dot);
  });
};

const probeImage = (urls) =>
  new Promise((resolve) => {
    const tryNext = (index) => {
      if (index >= urls.length) {
        resolve(null);
        return;
      }
      const img = new Image();
      img.onload = () => resolve(urls[index]);
      img.onerror = () => tryNext(index + 1);
      img.src = urls[index];
    };
    tryNext(0);
  });

const buildImagesFromFolder = async (card) => {
  const folder = card.dataset.folder;
  const exts = (card.dataset.exts || '.jpg,.JPG,.jpeg,.JPEG,.png,.PNG,.webp,.WEBP')
    .split(',')
    .map((ext) => ext.trim())
    .filter(Boolean);
  const explicitCount = Number(card.dataset.count || 0);
  const maxScan = Number(card.dataset.max || 10);
  if (!folder || !exts.length) return [];
  if (imageCache.has(folder)) {
    return imageCache.get(folder);
  }
  const results = [];
  const limit = explicitCount > 0 ? explicitCount : maxScan;
  for (let i = 1; i <= limit; i += 1) {
    const candidates = exts.map((ext) => `${folder}/${i}${ext}`);
    // eslint-disable-next-line no-await-in-loop
    const found = await probeImage(candidates);
    if (found) {
      results.push(found);
    } else if (!explicitCount) {
      break;
    }
  }
  imageCache.set(folder, results);
  return results;
};

const openSofaModal = async (card) => {
  const explicitImages = card.dataset.images;
  galleryState.images = explicitImages
    ? explicitImages.split(',')
    : await buildImagesFromFolder(card);
  galleryState.index = 0;
  modalTitle.textContent = card.dataset.title;
  modalPrice.textContent = card.dataset.price;
  modalDescription.textContent = card.dataset.description;
  
  // Build features list
  modalFeatures.innerHTML = '';
  const features = card.dataset.features ? card.dataset.features.split(',') : [];
  features.forEach(feature => {
    const li = document.createElement('li');
    li.textContent = feature.trim();
    modalFeatures.appendChild(li);
  });
  
  buildDots();
  updateGallery();
  if (galleryState.images.length) {
    openModal(sofaModal);
  }
};

// Scroll animations from template
const observerOptions = {
  threshold: 0.1,
  rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        observer.unobserve(entry.target);
      }
    });
  },
  observerOptions
);

// Observe elements with fade-in-up class
document.querySelectorAll('.fade-in-up').forEach((item) => observer.observe(item));

// Also observe elements with reveal class for backward compatibility
document.querySelectorAll('.reveal').forEach((item) => observer.observe(item));

// Header scroll effect
window.addEventListener('scroll', () => {
  if (window.scrollY > 50) {
    header.classList.add('scrolled');
  } else {
    header.classList.remove('scrolled');
  }
  
  if (window.scrollY > 500) {
    toTop.classList.add('show');
  } else {
    toTop.classList.remove('show');
  }
});

if (burger) {
  burger.addEventListener('click', () => {
    nav.classList.toggle('open');
    burger.classList.toggle('active');
  });
}

document.querySelectorAll('.nav a').forEach((link) => {
  link.addEventListener('click', () => {
    nav.classList.remove('open');
    burger.classList.remove('active');
  });
});

toTop.addEventListener('click', () => {
  window.scrollTo({ top: 0, behavior: 'smooth' });
});

const loadGalleryItems = async () => {
  const fallback = document.querySelector('#gallery-data');
  if (fallback && fallback.textContent.trim()) {
    try {
      return JSON.parse(fallback.textContent);
    } catch (error) {
      // eslint-disable-next-line no-console
      console.warn('Embedded gallery data is invalid.', error);
    }
  }

  try {
    const response = await fetch('data/gallery.json', { cache: 'no-store' });
    if (!response.ok) throw new Error('Gallery fetch failed');
    return await response.json();
  } catch (error) {
    // eslint-disable-next-line no-console
    console.warn('Gallery data is not available.', error);
    return [];
  }
};

const renderCards = async () => {
  if (!catalogGrid) return;
  const items = await loadGalleryItems();
  catalogGrid.innerHTML = '';

  if (!items.length) {
    catalogGrid.innerHTML = '<div class="catalog__empty">Галерея временно недоступна. Проверьте, что папка data и images загружены на хостинг.</div>';
    return;
  }

  const INITIAL_VISIBLE = 6; // 2 ряда по 3
  let allCards = [];

  for (const item of items) {
    const card = document.createElement('article');
    card.className = 'sofa-card fade-in-up';
    card.dataset.sofa = '';
    card.dataset.title = item.title || 'Без названия';
    card.dataset.price = item.price || '';
    card.dataset.description = item.description || '';
    card.dataset.folder = item.folder;

    // Extract features from description for modal
    const features = [];
    if (item.description) {
      const lines = item.description.split('\n');
      lines.forEach(line => {
        if (line.includes('общие габариты') || line.includes('спальное место')) {
          features.push(line.trim());
        }
      });
    }
    if (features.length > 0) {
      card.dataset.features = features.join(',');
    }

    if (item.exts) card.dataset.exts = item.exts;
    if (item.max) card.dataset.max = item.max;
    if (item.preview) card.dataset.preview = item.preview;

    card.innerHTML = `
      <div class="sofa-card__image"></div>
      <div class="sofa-card__body">
        <h3>${card.dataset.title}</h3>
        <p>${item.short || ''}</p>
        <div class="sofa-card__price">${card.dataset.price}</div>
      </div>
    `;

    catalogGrid.appendChild(card);
    observer.observe(card);
    allCards.push(card);
  }

  // Скрываем карточки после 6-й
  const hideExtraCards = () => {
    allCards.forEach((card, index) => {
      if (index >= INITIAL_VISIBLE) {
        card.style.display = 'none';
        card.classList.add('hidden-card');
      }
    });
  };

  hideExtraCards();

  // Обработчик кнопки "Показать все"
  const showMoreBtn = document.getElementById('show-more-btn');
  if (showMoreBtn) {
    showMoreBtn.addEventListener('click', () => {
      const isExpanded = showMoreBtn.classList.contains('is-active');
      
      if (isExpanded) {
        // Свернуть
        hideExtraCards();
        showMoreBtn.classList.remove('is-active');
        showMoreBtn.querySelector('span').textContent = 'Показать все диваны';
        document.querySelector('.catalog__scroll--vertical').style.maxHeight = 'none';
      } else {
        // Развернуть
        allCards.forEach((card, index) => {
          if (index >= INITIAL_VISIBLE) {
            setTimeout(() => {
              card.style.display = 'flex';
              card.style.opacity = '0';
              card.style.transform = 'translateY(20px)';
              setTimeout(() => {
                card.style.transition = 'all 0.4s ease';
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
              }, 50);
            }, (index - INITIAL_VISIBLE) * 100);
          }
        });
        showMoreBtn.classList.add('is-active');
        showMoreBtn.querySelector('span').textContent = 'Свернуть галерею';
      }
    });
  }

  const sofaCards = document.querySelectorAll('[data-sofa]');
  for (const card of sofaCards) {
    const preview = card.querySelector('.sofa-card__image');
    if (preview) {
      if (card.dataset.preview) {
        preview.style.backgroundImage = `url('${card.dataset.preview}')`;
      } else {
        const images = await buildImagesFromFolder(card);
        if (!images.length) {
          card.classList.add('is-hidden');
          continue;
        }
        preview.style.backgroundImage = `url('${images[0]}')`;
      }
    }
    card.addEventListener('click', () => openSofaModal(card));
  }
};

renderCards();

const modalButtons = document.querySelectorAll('[data-open-modal]');
modalButtons.forEach((btn) => {
  btn.addEventListener('click', () => {
    if (sofaModal.classList.contains('is-open')) {
      closeModal(sofaModal);
    }
    if (requestModal) {
      openModal(requestModal);
    }
  });
});

document.querySelectorAll('[data-close-modal]').forEach((btn) => {
  btn.addEventListener('click', () => {
    closeModal(sofaModal);
    closeModal(requestModal);
  });
});

document.querySelector('[data-gallery-prev]').addEventListener('click', (event) => {
  event.stopPropagation();
  galleryState.index = (galleryState.index - 1 + galleryState.images.length) % galleryState.images.length;
  updateGallery();
});

document.querySelector('[data-gallery-next]').addEventListener('click', (event) => {
  event.stopPropagation();
  galleryState.index = (galleryState.index + 1) % galleryState.images.length;
  updateGallery();
});

window.addEventListener('keydown', (event) => {
  if (event.key === 'Escape') {
    closeModal(sofaModal);
    closeModal(requestModal);
  }
});

[...document.querySelectorAll('.modal')].forEach((modal) => {
  modal.addEventListener('click', (event) => {
    if (event.target === modal) {
      closeModal(modal);
    }
  });
});

document.querySelectorAll('form').forEach((form) => {
  form.addEventListener('submit', (event) => {
    event.preventDefault();
    form.reset();
    if (requestModal && requestModal.classList.contains('is-open')) {
      closeModal(requestModal);
    }
  });
});
