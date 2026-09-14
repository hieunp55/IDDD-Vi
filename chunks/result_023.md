Vì bạn có thể sử dụng DAO (Data Access Object - đối tượng truy cập dữ liệu) và các pattern (mẫu thiết kế) liên quan để thực hiện những thao tác CRUD (Create, Read, Update, Delete - các thao tác cơ bản: Tạo, Đọc, Cập nhật, Xóa) chi tiết ở mức tinh thể trên dữ liệu mà đáng lẽ ra phải được coi là các phần cấu thành của một Aggregate (tập hợp các đối tượng nghiệp vụ ràng buộc theo một ranh giới nhất quán), nên đây là một pattern cần tránh đối với một domain model (mô hình miền nghiệp vụ). Trong điều kiện bình thường, bạn luôn muốn chính Aggregate tự quản lý logic nghiệp vụ cùng các thành phần nội bộ của nó và ngăn chặn mọi sự can thiệp từ bên ngoài.

Trước đây tôi từng chỉ ra rằng, đôi khi một stored procedure (thủ tục lưu trữ trong cơ sở dữ liệu) hoặc một data grid entry processor (bộ xử lý mục nhập trong lưới dữ liệu phân tán) là điều thiết yếu để đáp ứng một số nonfunctional requirement (yêu cầu phi chức năng) khắt khe. Tùy thuộc vào domain cụ thể của bạn, điều này có thể là quy luật chung hơn là ngoại lệ. Tuy nhiên, nếu một yêu cầu phi chức năng của hệ thống không bắt buộc điều đó, tôi khuyên bạn nên tránh sử dụng. Việc đặt và thực thi logic nghiệp vụ ngay trong data store (kho lưu trữ dữ liệu) nhiều khi đi ngược lại hoàn toàn với tinh thần của DDD (Domain-Driven Design - thiết kế hướng miền). Tôi có thể kết luận rằng việc sử dụng một Data Fabric Function/Entry Processor (hàm/bộ xử lý mục nhập của cấu trúc dữ liệu hợp nhất) thực chất không hề gây cản trở các mục tiêu của mô hình hóa miền. Phần triển khai Function/Entry Processor này có thể được viết bằng Java chẳng hạn, và vẫn hoàn toàn tuân thủ Ubiquitous Language (ngôn ngữ chung thống nhất) (1) cùng các mục tiêu của domain. Khác biệt duy nhất so với mô hình cốt lõi nằm ở nơi Function/Entry Processor được thực thi, và điều này không gây phá vỡ cấu trúc. Ngược lại, việc lạm dụng tràn lan các stored procedure lại tiềm ẩn nguy cơ phá vỡ DDD rất lớn, bởi vì ngôn ngữ lập trình của cơ sở dữ liệu thường không được nhóm mô hình hóa hiểu rõ, và các triển khai này thường được "giấu kỹ" khỏi tầm mắt của họ. Nếu như vậy, điều đó hoàn toàn trái ngược với những gì mà DDD đang nỗ lực đạt được.

> 💡 **Giải thích thêm:** Trong toán học và kỹ thuật phần mềm, cụm từ "runs orthogonal to" (chạy trực giao với) mang nghĩa là vuông góc, tách rời độc lập hoặc đi ngược lại hướng đi chính. Ở đây, tác giả muốn nhấn mạnh rằng việc đẩy logic nghiệp vụ xuống cơ sở dữ liệu đi ngược hoàn toàn với tôn chỉ của DDD — nơi logic miền phải là trung tâm và được thể hiện tường minh trong mã nguồn của ứng dụng.
> (Không có nguồn trích dẫn xác thực — cần tự kiểm chứng thêm)

Bạn có thể xem Repository (kho lưu trữ đối tượng miền nghiệp vụ) như một DAO theo nghĩa khái quát. Tuy nhiên, điều quan trọng cốt lõi cần ghi nhớ là hãy luôn cố gắng thiết kế các Repository theo định hướng tập hợp (collection orientation) thay vì định hướng truy cập dữ liệu (data access orientation). Điều đó sẽ giúp bạn duy trì sự tập trung vào domain dưới góc độ một mô hình, thay vì bị cuốn vào dữ liệu và các thao tác CRUD diễn ra ở hậu trường để phục vụ mục đích persistence (lưu trữ dữ liệu bền vững).

## Testing Repositories

Có hai góc độ khi xem xét việc kiểm thử Repository. Bạn phải kiểm thử chính bản thân các Repository để chứng minh rằng chúng hoạt động chính xác. Bạn cũng phải kiểm thử phần mã nguồn sử dụng Repository để lưu trữ các Aggregate vừa được tạo cũng như tìm kiếm các Aggregate đã tồn tại từ trước. Đối với loại kiểm thử thứ nhất, bạn bắt buộc phải sử dụng các triển khai hoàn chỉnh đạt chất lượng production (môi trường vận hành thực tế). Nếu không, bạn sẽ không thể biết được liệu mã nguồn production của mình có hoạt động hay không. Đối với loại kiểm thử thứ hai, bạn có thể sử dụng các triển khai production, hoặc thay thế bằng các triển khai in-memory (lưu trữ trong bộ nhớ). Lúc này tôi sẽ thảo luận về các bài kiểm thử cho triển khai production, và sẽ đề cập đến các bài kiểm thử in-memory ngay sau đó.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000490_9df635afd1abff62a7130e56334b0b6845d056abe7ee9dd1c1ddea4b08479a11.png)

Hãy cùng xem xét các bài kiểm thử cho phần triển khai Coherence của `ProductRepository` đã được trình bày trước đó:

```java
public class CoherenceProductRepositoryTest extends DomainTest {

    private ProductRepository productRepository;
    private TenantId tenantId;

    public CoherenceProductRepositoryTest() {
        super();
    }

    // ...

    @Override
    protected void setUp() throws Exception {
        this.setProductRepository(new CoherenceProductRepository());
        this.tenantId = new TenantId("01234567");
        super.setUp();
    }

    @Override
    protected void tearDown() throws Exception {
        Collection<Product> products =
            this.productRepository().allProductsOfTenant(tenantId);
        this.productRepository().removeAll(products);
    }

    protected ProductRepository productRepository() {
        return this.productRepository;
    }

    protected void setProductRepository(ProductRepository aProductRepository) {
        this.productRepository = aProductRepository;
    }
}

```

Có một số thao tác setup (thiết lập chuẩn bị) và tear-down (dọn dẹp) chung để sẵn sàng cho mỗi bài kiểm thử và dọn dẹp sau khi hoàn tất. Để thiết lập, chúng ta tạo một thể hiện của lớp `CoherenceProductRepository` và sau đó tạo một thể hiện giả của `TenantId` (định danh đơn vị thuê trong kiến trúc đa người thuê).

Để dọn dẹp, chúng ta xóa tất cả các thể hiện `Product` có thể đã được thêm vào bộ nhớ cache phía sau bởi từng bài kiểm thử. Đối với Coherence, đây là một bước dọn dẹp rất quan trọng. Nếu bạn không xóa hết các thể hiện đã được lưu trong cache, chúng sẽ tiếp tục tồn tại trong các bài kiểm thử tiếp theo, điều này có thể dẫn đến thất bại ở một số assertion (phép khẳng định kiểm thử) nhất định, chẳng hạn như phép đếm số lượng thể hiện được lưu trữ.

Tiếp theo, chúng ta kiểm thử hành vi của Repository:

```java
public class CoherenceProductRepositoryTest extends DomainTest {

    // ...

    public void testSaveAndFindOneProduct() throws Exception {
        Product product = new Product(
            tenantId,
            this.productRepository().nextIdentity(),
            "My Product",
            "This is the description of my product.");

        this.productRepository().save(product);

        Product readProduct =
            this.productRepository().productOfId(tenantId, product.productId());

        assertNotNull(readProduct);
        assertEquals(readProduct.tenantId(), tenantId);
        assertEquals(readProduct.productId(), product.productId());
        assertEquals(readProduct.name(), product.name());
        assertEquals(readProduct.description(), product.description());
    }

    // ...
}

```

Đúng như tên của phương thức kiểm thử đã thể hiện, ở đây chúng ta lưu một `Product` đơn lẻ và cố gắng tìm lại nó. Nhiệm vụ đầu tiên là khởi tạo một `Product` và sau đó lưu nó vào Repository. Nếu tầng hạ tầng không ném ra ngoại lệ nào, chúng ta có thể nghĩ rằng `Product` đã được lưu thành công. Tuy nhiên, chỉ có một cách duy nhất để biết chắc chắn: chúng ta phải tìm lại thể hiện đó và so sánh với bản gốc. Để tìm thể hiện này, chúng ta truyền định danh duy nhất toàn cầu của nó vào phương thức `productOfId()`. Nếu tìm thấy thể hiện, chúng ta có thể khẳng định thành công rằng nó không bị null, `tenantId` của nó trùng khớp, `productId` trùng khớp, `name` trùng khớp, và `description` hoàn toàn giống với đối tượng đã được lưu trữ.

Tiếp theo, chúng ta kiểm thử việc lưu và tìm kiếm nhiều thể hiện:

```java
public class CoherenceProductRepositoryTest extends DomainTest {

    // ...

    public void testSaveAndFindMultipleProducts() throws Exception {

```

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000491_7197cb8c9ea745059992848ae6de6b2f78f543ca816969eb8b1dde2e0f9edd3a.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000492_ff9a91d7fb0312764133f571d8a18078436c0792d1028276151d0835bb13858f.png)

## Chapter 12 REPOSITORIES

```java
        Product product1 = new Product(
            tenantId,
            this.productRepository().nextIdentity(),
            "My Product 1",
            "This is the description of my first product.");

        Product product2 = new Product(
            tenantId,
            this.productRepository().nextIdentity(),
            "My Product 2",
            "This is the description of my second product.");

        Product product3 = new Product(
            tenantId,
            this.productRepository().nextIdentity(),
            "My Product 3",
            "This is the description of my third product.");

        this.productRepository()
            .saveAll(Arrays.asList(product1, product2, product3));

        assertNotNull(this.productRepository()
            .productOfId(tenant, product1.productId()));
        assertNotNull(this.productRepository()
            .productOfId(tenant, product2.productId()));
        assertNotNull(this.productRepository()
            .productOfId(tenant, product3.productId()));

        Collection<Product> allProducts =
            this.productRepository().allProductsOfTenant(tenant);

        assertEquals(allProducts.size(), 3);
    }

    // ...
}

```

Đầu tiên, chúng ta khởi tạo ba thể hiện `Product` và sau đó lưu chúng cùng lúc bằng `saveAll()`. Tiếp theo, chúng ta lại sử dụng `productOfId()` để tìm từng thể hiện riêng lẻ. Nếu cả ba thể hiện đều không null, chúng ta có thể tin tưởng rằng cả ba thể hiện đã được lưu trữ bền vững một cách chính xác.

## Cowboy Logic

* AJ: "Chị gái tôi kể rằng anh rể dặn chị ấy bán sạch đồ đạc trong kho của anh đi khi anh qua đời. Chị tôi hỏi lý do tại sao. Anh ấy bảo không muốn một gã dở hơi nào đó xài đồ của mình khi chị tái giá. Chị tôi bảo anh đừng lo, vì chị chẳng dại gì mà đi lấy một gã dở hơi khác nữa đâu."

> 💡 **Giải thích thêm:** Câu chuyện ngụ ngôn hài hước của cao bồi AJ vừa là lời châm biếm hóm hỉnh, vừa ẩn dụ cho việc dọn dẹp sạch sẽ kho lưu trữ/cache (tear-down) sau mỗi bài test: nếu không dọn dẹp dữ liệu cũ sau khi xong việc, mớ đồ đạc tồn đọng sẽ rơi vào tay kẻ khác (tiến trình test tiếp theo) và gây ra những rắc rối không lường trước.
> (Không có nguồn trích dẫn xác thực — cần tự kiểm chứng thêm)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000493_44efe1f03378dba8abe145ffca793e2ecdfa2fafaa5ee3d5f6ef2a6502f2f984.png)

Còn một phương thức của Repository là `allProductsOfTenant()` vẫn chưa được kiểm thử. Vì bộ nhớ cache của Repository hoàn toàn trống khi bài test bắt đầu, chúng ta phải đọc thành công ba thể hiện `Product` từ đó. Do đó, chúng ta sẽ cố gắng tìm kiếm tất cả chúng. `Collection` được trả về không bao giờ được phép null, ngay cả khi bạn không tìm thấy những gì mình mong đợi. Vì vậy, bước cuối cùng trong bài test là khẳng định rằng toàn bộ số lượng thể hiện `Product` kỳ vọng — tức là ba — trên thực tế đã được tìm thấy.

Bây giờ khi đã có một bài test chứng minh cách các client có thể sử dụng Repository và xác thực tính đúng đắn của nó, chúng ta có thể xem xét cách kiểm thử tối ưu hơn cho các client sử dụng Repository.

## Testing with In-Memory Implementations

Nếu việc thiết lập triển khai lưu trữ bền vững hoàn chỉnh của một Repository cho bài kiểm thử là quá phức tạp hoặc quá chậm chạp khi thực thi, bạn có thể tận dụng một hướng tiếp cận khác. Bạn cũng có thể đối mặt với những điều kiện không mong muốn trong giai đoạn đầu mô hình hóa miền, chẳng hạn như khi các cơ chế lưu trữ bền vững — bao gồm cả database schema (lược đồ cơ sở dữ liệu) — vẫn chưa sẵn sàng. Khi rơi vào bất kỳ tình huống nào trong số này, giải pháp hiệu quả nhất là triển khai một phiên bản in-memory cho các Repository.

Việc tạo các phiên bản in-memory có thể khá đơn giản, nhưng đôi khi cũng đặt ra một số thách thức. Phần đơn giản là tạo một `HashMap` làm nền tảng cho interface của bạn. Việc thực hiện `put()` các mục vào và `remove()` chúng khỏi `Map` là rất rõ ràng và dễ dàng. Chúng ta chỉ cần sử dụng định danh duy nhất toàn cầu của mỗi thể hiện Aggregate làm key. Bản thân thể hiện Aggregate sẽ đóng vai trò là value. Các phương thức `add()` hoặc `save()` và các phương thức `remove()` đều rất đơn giản. Trên thực tế, đối với trường hợp của `ProductRepository`, toàn bộ phần triển khai diễn ra khá nhẹ nhàng:

```java
package com.saasovation.agilepm.domain.model.product.impl;

public class InMemoryProductRepository implements ProductRepository {

    private Map<ProductId, Product> store;

    public InMemoryProductRepository() {
        super();
        this.store = new HashMap<ProductId, Product>();
    }

    @Override
    public Collection<Product> allProductsOfTenant(Tenant aTenant) {
        Set<Product> entries = new HashSet<Product>();

        for (Product product : this.store.values()) {
            if (product.tenant().equals(aTenant)) {
                entries.add(product);
            }
        }

```

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000494_4ec904ecec8e97759df9d01a22b5c5ba9191703d0ef23b05b264a9a5663a9308.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000495_f46c8eb048150362af38081c3581ecf69d198f73c1d2ee27b66cbd87ff3426e6.png)

```java
        return entries;
    }

    @Override
    public ProductId nextIdentity() {
        return new ProductId(java.util.UUID.randomUUID()
            .toString().toUpperCase());
    }

    @Override
    public Product productOfId(Tenant aTenant, ProductId aProductId) {
        Product product = this.store.get(aProductId);

        if (product != null) {
            if (!product.tenant().equals(aTenant)) {
                product = null;
            }
        }

        return product;
    }

    @Override
    public void remove(Product aProduct) {
        this.store.remove(aProduct.productId());
    }

    @Override
    public void removeAll(Collection<Product> aProductCollection) {
        for (Product product : aProductCollection) {
            this.remove(product);
        }
    }

    @Override
    public void save(Product aProduct) {
        this.store.put(aProduct.productId(), aProduct);
    }

    @Override
    public void saveAll(Collection<Product> aProductCollection) {
        for (Product product : aProductCollection) {
            this.save(product);
        }
    }
}

```

Trên thực tế, chỉ có duy nhất một trường hợp đặc biệt đối với `productOfId()`. Để triển khai bộ tìm kiếm (finder) này một cách chính xác, sau khi lấy được `Product` khớp với `ProductId` đã cho, chúng ta cũng phải kiểm tra xem `TenantId` của `Product` đó có khớp với tham số `Tenant` hay không. Nếu không khớp, chúng ta gán thể hiện `Product` đó thành `null`.

Chúng ta hoàn toàn có thể tạo một bản sao gần như giống hệt của `CoherenceProductRepositoryTest` mang tên `InMemoryProductRepositoryTest` để kiểm thử phần triển khai in-memory này. Thay đổi duy nhất cần thực hiện nằm ở phương thức `setUp()`:

```java
public class InMemoryProductRepositoryTest extends TestCase {

    // ...

    @Override
    protected void setUp() throws Exception {
        this.setProductRepository(new InMemoryProductRepository());
        this.tenantId = new TenantId("01234567");
        super.setUp();
    }

    // ...
}

```

Chỉ cần khởi tạo `InMemoryProductRepository` thay vì triển khai Coherence. Ngoài điểm đó ra, bản thân các phương thức kiểm thử hoàn toàn giống hệt nhau.

Những thách thức khó khăn có thể phát sinh thường liên quan đến việc triển khai các finder nâng cao hơn, nơi các tiêu chí tham số rất phức tạp để phân giải. Nếu các tiêu chí và logic xử lý tìm kiếm trở nên quá phức tạp, bạn có thể phải tìm giải pháp thay thế. Điều này có thể đồng nghĩa với việc nạp sẵn dữ liệu (prepopulating) vào Repository bằng các thể hiện sẽ đáp ứng được tìm kiếm, trong khi bản thân phương thức finder chỉ trả về đúng thể hiện hoặc các thể hiện đã được nạp sẵn đó. Bạn có thể nạp sẵn dữ liệu bằng cách sử dụng phương thức `setUp()` của bài kiểm thử.

Một ưu điểm khác của việc triển khai các phiên bản in-memory cho Repository là khi bạn cần kiểm thử việc sử dụng đúng đắn phương thức `save()` với một interface định hướng lưu trữ bền vững (persistence-oriented interface). Bạn có thể triển khai các phương thức `save()` để đếm số lần được gọi. Sau khi mỗi bài test chạy xong, bạn có thể assert xem số lần gọi có khớp với số lượng mà client của Repository cụ thể đó yêu cầu hay không. Thông thường, bạn có thể áp dụng cách tiếp cận này khi kiểm thử các Application Service (dịch vụ tầng ứng dụng) vốn phải thực hiện thao tác `save()` tường minh các thay đổi vào một Aggregate.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000496_b030eabea36541d9d0570e573d7f3eb86fe5c8683d746afe1177a9d8e3e40624.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000497_14db21ce1e00be49fe18c10709838b49eee9a14826f145ab6853020e91b4fa29.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000498_881f4be078c88636ccf75d6188bb37bf260a529a9e182bae5152961d266c9f28.png)

## Wrap-Up

Trong chương này, chúng ta đã xem xét chuyên sâu về việc triển khai các Repository.

* Bạn đã tìm hiểu về Repository định hướng tập hợp và định hướng lưu trữ bền vững, cũng như lý do khi nào nên sử dụng loại này hay loại kia.
* Bạn đã thấy cách triển khai Repository cho Hibernate, TopLink, Coherence và MongoDB.
* Bạn đã khám phá lý do tại sao bạn có thể cần thêm các hành vi bổ sung trên interface của Repository.
* Bạn đã cân nhắc vai trò của transaction (giao dịch) trong việc sử dụng Repository.
* Giờ đây bạn đã quen thuộc với những thách thức khi thiết kế Repository cho các hệ thống phân cấp kiểu dữ liệu.
* Bạn đã xem xét một số điểm khác biệt căn bản giữa Repository và Data Access Object.
* Bạn đã thấy cách kiểm thử Repository và các phương pháp kiểm thử khác nhau khi sử dụng Repository.

Tiếp theo, chúng ta sẽ chuyển hướng và xem xét cẩn trọng việc tích hợp các Bounded Context.

## Chapter 13

## Integrating Bounded Contexts

Việc tạo ra các kết nối tư duy là công cụ học tập quan trọng nhất của chúng ta, là bản chất của trí tuệ con người; để rèn giũa các liên kết; để vượt ra ngoài những gì đã có; để nhìn ra các khuôn mẫu, các mối quan hệ, và bối cảnh.

* Marilyn Ferguson

Luôn luôn tồn tại nhiều Bounded Context (ngữ cảnh giới hạn) (2) trong bất kỳ dự án có quy mô đáng kể nào, và hai hoặc nhiều Bounded Context trong số đó sẽ cần phải tích hợp với nhau. Thông qua Context Map (bản đồ ngữ cảnh) (3), chúng ta đã thảo luận về các mối quan hệ thường tồn tại giữa các Bounded Context, đồng thời kiểm tra một số cách thức quản lý đúng đắn các mối quan hệ đó theo các nguyên tắc của DDD. Nếu bạn chưa nắm vững kiến thức về Domain (2), Subdomain (miền con) (2), và Bounded Context, hoặc về Context Map, bạn nên tìm hiểu kỹ trước khi tiếp tục. Nội dung được trình bày ở đây được xây dựng dựa trên những khái niệm nền tảng đó.

Như đã thảo luận trước đây, Context Map có hai dạng thức chính. Một dạng là bản vẽ đơn giản được sử dụng để minh họa các kiểu quan hệ tồn tại giữa hai hay nhiều Bounded Context bất kỳ. Dạng thứ hai, cụ thể hơn rất nhiều, chính là mã nguồn thực sự hiện thực hóa các mối quan hệ đó. Đó chính là điều chúng ta đang xem xét lúc này.

## Road Map to This Chapter

* Ôn lại một số kiến thức cơ bản về tích hợp, và xây dựng tư duy đúng đắn cần thiết để thành công trong việc tích hợp các hệ thống trong môi trường tính toán phân tán.
* Xem xét cách bạn có thể tiếp cận việc tích hợp bằng tài nguyên RESTful (kiểu kiến trúc truyền trạng thái đại diện qua HTTP), đồng thời cân nhắc một số ưu điểm và nhược điểm của nó.
* Tìm hiểu cách tích hợp khi sử dụng cơ chế truyền thông điệp (messaging).
* Thấu hiểu những thách thức bạn sẽ phải đối mặt khi quyết định sao chép trùng lặp thông tin giữa các Bounded Context.
* Nghiên cứu các ví dụ mang lại mức độ trưởng thành ngày càng cao trong các phương pháp tiếp cận thiết kế.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000499_eb8a30e0d6511c27aaf1966ed0cfe3f3684eb481f4b8076927190947e8013e48.png)

## Integration Basics

Khi hai Bounded Context cần tích hợp, có một vài cách tương đối rõ ràng để thực hiện điều này trong mã nguồn.

Một phương pháp trực tiếp như vậy là để một Bounded Context cung cấp một giao diện lập trình ứng dụng (API), và Bounded Context khác sẽ sử dụng API đó thông qua các RPC (Remote Procedure Call - gọi thủ tục từ xa). API này có thể được cung cấp bằng SOAP hoặc chỉ đơn giản là hỗ trợ gửi các yêu cầu và phản hồi XML qua HTTP (không hoàn toàn giống với REST). Thực tế có một vài cách để tạo ra một API có thể truy cập từ xa. Đây là một trong những cách tích hợp phổ biến hơn, và vì nó hỗ trợ phong cách gọi thủ tục, nó rất dễ hiểu đối với các lập trình viên vốn đã quen thuộc với việc gọi hàm hoặc phương thức — điều mà hầu hết chúng ta đều đã làm quen.

Cách thứ hai để tích hợp các Bounded Context là thông qua việc sử dụng cơ chế truyền thông điệp. Mỗi hệ thống cần tương tác sẽ thực hiện điều đó thông qua việc sử dụng hàng đợi thông điệp (message queue) hoặc cơ chế Publish-Subscribe (Xuất bản - Đăng ký) [Gamma et al.]. Dĩ nhiên, các cổng giao tiếp thông điệp này hoàn toàn có thể được xem như một API, nhưng chúng ta có thể nhận được sự đồng thuận rộng rãi hơn nếu gọi chúng đơn giản là các service interface (giao diện dịch vụ). Có một lượng lớn các kỹ thuật tích hợp có thể được áp dụng khi sử dụng messaging, nhiều kỹ thuật trong số đó đã được thảo luận trong [Hohpe & Woolf].

Cách thứ ba để tích hợp các Bounded Context là sử dụng RESTful HTTP. Một số người nghĩ về điều này như một dạng tiếp cận RPC, nhưng thực chất không phải. Nó có một vài thuộc tính tương đồng ở chỗ một hệ thống gửi yêu cầu đến hệ thống khác, nhưng các yêu cầu này không được thực hiện thông qua các thủ tục nhận tham số. Như đã thảo luận trong chương Architecture (Kiến trúc) (4), REST là một phương thức trao đổi và sửa đổi các tài nguyên (resources) được định danh duy nhất bằng một URI xác định. Nhiều thao tác khác nhau có thể được thực hiện trên từng tài nguyên. RESTful HTTP cung cấp các phương thức, chủ yếu là `GET`, `PUT`, `POST`, và `DELETE`. Mặc dù những phương thức này dường như chỉ hỗ trợ các thao tác CRUD, một chút sáng tạo cho phép chúng ta phân loại các thao tác với chủ đích nghiệp vụ rõ ràng vào một trong bốn nhóm phương thức đó. Ví dụ, `GET` có thể được dùng để phân loại nhiều dạng thao tác truy vấn khác nhau, và `PUT` có thể dùng để đóng gói một thao tác command thực thi trên một Aggregate (10).

Dĩ nhiên, điều này không có nghĩa là chỉ có ba cách duy nhất để tích hợp các ứng dụng. Ví dụ, bạn có thể sử dụng tích hợp dựa trên tệp (file-based integration) và tích hợp dùng chung cơ sở dữ liệu (shared-database integration), nhưng làm như vậy có thể khiến bạn già trước tuổi.

## Cowboy Logic

AJ: "Tốt nhất là anh nên ngồi vững trên yên ngựa đi. Con ngựa đó dữ dằn lắm đấy, nó sẽ khiến anh già trước tuổi cho mà xem."

> 💡 **Giải thích thêm:** Thành ngữ "make you old before your time" (khiến bạn già trước tuổi) ý chỉ sự kiệt sức và căng thẳng tột độ. AJ dùng hình ảnh cưỡi ngựa bất kham ("take a low seat in your saddle" - hạ thấp trọng tâm trên yên ngựa) để cảnh báo: nếu chọn các phương thức tích hợp cổ hủ và nhiều cạm bẫy như dùng chung database hay chia sẻ file, bạn sẽ phải trả giá bằng vô số đêm mất ngủ để sửa lỗi và bảo trì.
> (Không có nguồn trích dẫn xác thực — cần tự kiểm chứng thêm)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000500_a5f3fd6d6c2c83d45eec67e12f7ad36e463df16f4131adb4d0251c5abc9ae45a.png)

Mặc dù tôi đã nêu bật ba cách phổ biến được sử dụng để tích hợp các Bounded Context, chúng ta thực tế sẽ chỉ tập trung vào hai cách trong số đó xuyên suốt chương này. Chúng ta sẽ chủ yếu tập trung vào việc tích hợp với các cơ chế messaging, nhưng cũng sẽ xem xét cách sử dụng RESTful HTTP. Chúng ta sẽ tránh các ví dụ sử dụng RPC vì bạn có thể dễ dàng hình dung việc tạo ra các API thủ tục thay thế cho hai hướng tiếp cận còn lại. Ngoài ra, RPC có tính kiên cường (resilience) kém hơn khi mục tiêu của chúng ta là hỗ trợ các autonomous service (dịch vụ tự trị, hay còn gọi là các ứng dụng tự trị). Một hệ thống gặp sự cố mà thông thường vốn cung cấp API dựa trên RPC sẽ khiến các hệ thống phụ thuộc vào nó không thể hoàn thành các thao tác của chính chúng.

Điều này dẫn đến một chủ đề mang tầm quan trọng sống còn, đòi hỏi sự lưu tâm của mọi lập trình viên làm công việc tích hợp.

## Distributed Systems Are Fundamentally Different

Các vấn đề luôn phát sinh trong quá trình tích hợp khi các lập trình viên chưa quen thuộc với các nguyên lý của hệ thống phân tán xem nhẹ sự phức tạp vốn có của nó. Điều này đặc biệt đúng khi sử dụng RPC, bởi vì những người thiếu kinh nghiệm với hệ thống phân tán thường mặc định rằng bất kỳ lệnh gọi từ xa nào cũng tốt tương đương với một lệnh gọi nội bộ trong cùng tiến trình (in-process). Những giả định như vậy có thể gây ra lỗi dây chuyền (cascading failure) trên hàng loạt hệ thống khi chỉ một hệ thống hoặc một trong các thành phần của nó trở nên không khả dụng, ngay cả khi chỉ mang tính tạm thời. Vì vậy, tất cả các lập trình viên làm việc trong các hệ thống phân tán sẽ thành công hay thất bại dựa trên các Nguyên lý Tính toán Phân tán (Principles of Distributed Computing) sau đây:

* Mạng không hề đáng tin cậy.
* Luôn luôn có độ trễ nhất định, và đôi khi độ trễ là rất lớn.
* Băng thông không phải là vô hạn.
* Đừng bao giờ giả định mạng là an toàn.
* Cấu trúc liên kết mạng (topology) luôn thay đổi.
* Kiến thức và chính sách bị phân tán qua nhiều quản trị viên khác nhau.
* Chi phí vận chuyển qua mạng luôn tồn tại.
* Mạng mang tính chất không đồng nhất.

Những điều này được chủ ý phát biểu khác đi so với "Các ngụy biện của tính toán phân tán" (Fallacies of Distributed Computing) [Deutsch]. Tôi gọi chúng là các nguyên lý để nhấn mạnh vào những thách thức cần phải vượt qua và những độ phức tạp cần phải được lên kế hoạch dự phòng, thay vì xem chúng là những sai lầm thường thấy của những người ngây thơ.

> 💡 **Giải thích thêm:** "8 Ngụy biện của Tính toán Phân tán" (Fallacies of Distributed Computing) là danh sách kinh điển do kiến trúc sư L. Peter Deutsch cùng các đồng nghiệp tại Sun Microsystems tổng kết từ năm 1994, cảnh báo các giả định sai lầm tai hại mà giới lập trình thường mắc phải khi chuyển từ hệ thống đơn khối (monolith) sang hệ thống phân tán.
> Nguồn tham khảo: https://en.wikipedia.org/wiki/Fallacies_of_distributed_computing

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000501_d6987f0a2a350cff2c29be3e63cfd359d01da7bf49ab00adb72e581fb790e5d4.png)

## Exchanging Information across System Boundaries

Phần lớn thời gian khi chúng ta cần một hệ thống bên ngoài cung cấp dịch vụ cho hệ thống của mình, chúng ta cần truyền dữ liệu thông tin tới dịch vụ đó. Các dịch vụ chúng ta sử dụng đôi khi cần trả về phản hồi. Do đó, chúng ta cần một phương thức đáng tin cậy để truyền dữ liệu thông tin giữa các hệ thống. Dữ liệu này cần được trao đổi giữa các hệ thống khác biệt về bản chất theo một cấu trúc mà tất cả các bên liên quan đều có thể dễ dàng tiêu thụ. Hầu hết chúng ta sẽ chọn một cách thức chuẩn mực nào đó để làm điều này.

Dữ liệu thông tin được gửi dưới dạng tham số hoặc thông điệp chỉ cấu thành các cấu trúc mà máy móc có thể đọc được và có thể được tạo ra theo một trong nhiều định dạng. Chúng ta cũng phải tạo ra một dạng hợp đồng (contract) giữa các hệ thống trao đổi dữ liệu, và thậm chí có thể cả các cơ chế để phân tích cú pháp (parse) hoặc diễn giải các cấu trúc đó nhằm phục vụ việc tiêu thụ.

Có một vài cách để tạo ra các cấu trúc được dùng để trao đổi thông tin giữa các hệ thống. Một cách triển khai kỹ thuật chỉ đơn giản dựa vào các tính năng của ngôn ngữ lập trình để serialize (tuần tự hóa) các đối tượng thành định dạng nhị phân và deserialize (giải tuần tự hóa) chúng ở phía bên tiêu thụ. Cách này hoạt động tốt miễn là tất cả các hệ thống đều hỗ trợ cùng một bộ tính năng ngôn ngữ, và nếu quá trình serialization thực sự tương thích hoặc có thể hoán đổi giữa các kiến trúc phần cứng khác biệt. Nó cũng đòi hỏi bạn phải deploy (triển khai) tất cả các interface và class của các đối tượng được sử dụng giữa các hệ thống tới từng hệ thống có sử dụng kiểu đối tượng cụ thể đó.

Một hướng tiếp cận khác để xây dựng các cấu trúc thông tin có thể trao đổi là sử dụng một định dạng trung gian tiêu chuẩn nào đó. Một số lựa chọn là sử dụng XML, JSON, hoặc một định dạng chuyên biệt như Protocol Buffers (giao thức tuần tự hóa dữ liệu nhị phân). Mỗi hướng tiếp cận này đều có những ưu điểm và nhược điểm riêng, bao gồm các yếu tố về mức độ phong phú và tính tinh gọn, hiệu năng chuyển đổi kiểu dữ liệu, khả năng hỗ trợ tính linh hoạt giữa các phiên bản đối tượng, và tính dễ sử dụng. Một số yếu tố này có thể gây ra những tác động tốn kém khi cân nhắc đến các Nguyên lý Tính toán Phân tán đã liệt kê trước đó (chẳng hạn như "Chi phí vận chuyển qua mạng luôn tồn tại").

Sử dụng phương pháp định dạng trung gian này, bạn vẫn có thể muốn deploy toàn bộ các interface và class của các đối tượng được sử dụng xuyên suốt các hệ thống, đồng thời sử dụng một công cụ để ánh xạ dữ liệu từ định dạng trung gian vào các đối tượng type-safe (an toàn kiểu dữ liệu) của bạn. Điều này mang lại lợi thế là bạn có thể sử dụng các đối tượng trong hệ thống tiêu thụ theo cách hoàn toàn tương tự như bạn làm trong hệ thống nguồn.

Dĩ nhiên, việc deploy các interface và class này cũng đi kèm với độ phức tạp liên quan, và nó thường đồng nghĩa với việc hệ thống tiêu thụ sẽ cần phải được biên dịch lại (recompile) để duy trì khả năng tương thích với các phiên bản mới nhất của định nghĩa interface và class. Ngoài ra còn có nguy cơ sử dụng tùy tiện các đối tượng ngoại lai trong hệ thống tiêu thụ như thể chúng là đối tượng của chính mình, điều này thường có xu hướng vi phạm chính các nguyên lý thiết kế chiến lược của DDD mà chúng ta đã dày công gìn giữ. Một số người có thể nghĩ rằng bằng cách khai báo điều này như một Shared Kernel (hạt nhân chia sẻ) (3), họ đã hợp thức hóa được cách tiếp cận này. Tuy nhiên, hãy lưu ý rằng sự tiện lợi của các đối tượng được chia sẻ giữa các hệ thống có thể dẫn bạn xuống một con dốc trượt nguy hiểm. Dẫu vậy, bất chấp sự phức tạp và mối nguy tiềm ẩn về việc làm ô nhiễm mô hình, nhiều người vẫn tin rằng tính an toàn kiểu mạnh mẽ có được từ chiến thuật này là một sự đánh đổi hoàn toàn thỏa đáng cho độ phức tạp bắt buộc phải có.

> 💡 **Giải thích thêm:** "Slippery slope" (con dốc trượt) là thành ngữ chỉ chuỗi sự kiện mà khi đã bước một bước nhỏ tưởng chừng vô hại (ở đây là chia sẻ chung các class/interface giữa các hệ thống), ta rất dễ trượt dài và khó dừng lại, cuối cùng dẫn đến việc hai mô hình bị phụ thuộc chằng chịt vào nhau và phá vỡ ranh giới độc lập của các Bounded Context.
> (Không có nguồn trích dẫn xác thực — cần tự kiểm chứng thêm)

Tuy nhiên, tôi vẫn thường xuyên gặp những người phải vật lộn với vấn đề này vì nhiều lý do khác nhau, và họ thường mong ước một cách tiếp cận dễ dàng và an toàn hơn, nhưng không hoàn toàn vứt bỏ tính an toàn kiểu dữ liệu. Hãy cùng xem xét một cách tiếp cận như vậy.

Sẽ ra sao nếu chúng ta có thể định nghĩa một bản hợp đồng giữa các hệ thống tạo ra các cấu trúc thông tin có thể trao đổi và các hệ thống tiêu thụ chúng theo cách mà các bên tiêu thụ có thể tự tin sử dụng dữ liệu mà không cần phải giải tuần tự hóa nó thành các thể hiện đối tượng của các class cụ thể? Chúng ta có thể định nghĩa một hợp đồng đáng tin cậy như vậy bằng cách sử dụng phương pháp dựa trên tiêu chuẩn, vốn thực chất hình thành nên một Published Language (ngôn ngữ được công bố) (3). Một phương pháp tiêu chuẩn như vậy là định nghĩa một custom media type (kiểu phương tiện tùy biến), hoặc khái niệm tương đương về mặt ngữ nghĩa. Cho dù bạn có lý do xác đáng để đăng ký một media type như vậy theo các hướng dẫn từ RFC 4288 hay không, thì điều thực sự quan trọng chính là bản đặc tả kỹ thuật thực tế. Bản đặc tả này xác định hợp đồng ràng buộc giữa bên sản xuất (producer) và bên tiêu thụ (consumer), đồng thời cung cấp một phương tiện chắc chắn để trao đổi các loại dữ liệu đa phương tiện đó mà không cần chia sẻ các tệp nhị phân chứa interface và class.

Điều này đòi hỏi một số sự đánh đổi, như thường lệ. Bạn sẽ không thể điều hướng bằng cách sử dụng các hàm truy xuất thuộc tính (accessor) như khi sở hữu các interface/class cho từng đối tượng cùng với tính an toàn kiểu dữ liệu đi kèm. Bạn cũng sẽ thiếu đi sự hỗ trợ từ IDE, chẳng hạn như khả năng tự động hoàn thành mã nguồn (code completion). Đây thực ra không phải là một nhược điểm quá lớn. Hơn nữa, bạn sẽ không nhận được sự hỗ trợ từ các function/method vận hành mà một class Event có thể cung cấp. Tuy nhiên, tôi không nhìn nhận việc thiếu vắng các function/method vận hành của Event là một nhược điểm, mà coi đó là một cơ chế bảo vệ. Bounded Context tiêu thụ chỉ nên quan tâm đến các thuộc tính dữ liệu và tuyệt đối không bao giờ được phép bị cám dỗ sử dụng các chức năng vốn là một phần của một mô hình khác. Các Port and Adapter (Cổng và Bộ điều hợp) (4) của bên tiêu thụ cần phải che chắn cho mô hình miền của nó khỏi bất kỳ sự phụ thuộc nào như vậy, và thay vào đó phải truyền dữ liệu Event cần thiết dưới dạng các tham số phù hợp với các kiểu dữ liệu chỉ được định nghĩa bên trong chính Bounded Context của nó. Mọi tính toán hoặc xử lý cần thiết phải do Bounded Context sản xuất thực hiện và cung cấp dưới dạng các thuộc tính dữ liệu Event được làm giàu thêm.

Hãy xem xét một ví dụ. SaaSOvation cần trao đổi dữ liệu media giữa các Bounded Context khác nhau của mình. Hệ thống sẽ thực hiện điều đó bằng cách sử dụng các tài nguyên RESTful và gửi các thông điệp chứa các Event (sự kiện miền nghiệp vụ) (8) giữa các service. Trên thực tế, một dạng tài nguyên RESTful là một notification (thông báo), và các thông điệp dựa trên Event cũng được gửi tới các subscriber dưới dạng các đối tượng `Notification`. Nói cách khác, trong cả hai trường hợp, `Notification` đều chứa một Event, và cả hai được định dạng thành một cấu trúc duy nhất. Bản đặc tả custom media type cho các notification và Event có thể chỉ ra một bản hợp đồng bao gồm:

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000502_24dd1392ad540226212087ebe394b17889360101e61373d0264d429016acfe74.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000503_c7014e1c3c80c99f2da039ee66c9bcfbf814e71a18e6cf199ea2a441d691b300.png)

## Chapter 13 INTEGRATING BOUNDED CONTEXTS

* Type: Định dạng Notification: JSON
* `notificationId`: Định danh duy nhất kiểu số nguyên long
* `typeName`: Chuỗi text String chỉ kiểu của thông báo, một ví dụ về tên kiểu là `com.saasovation.agilepm.domain.model.product.backlogItem.BacklogItemCommitted`
* `version`: Phiên bản kiểu số nguyên của thông báo
* `occurredOn`: Ngày/giờ khi Event chứa trong thông báo xảy ra
* `event`: Chi tiết payload JSON; xem các kiểu Event cụ thể

Việc sử dụng tên lớp đủ điều kiện (fully qualified class name - bao gồm cả tên package) cho `typeName` cho phép các subscriber phân biệt chính xác các kiểu `Notification` khác nhau. Bản đặc tả thông báo sẽ được tiếp nối bởi các bản đặc tả của từng kiểu Event khác nhau. Lấy một ví dụ, hãy xem xét một Event quen thuộc mang tên `BacklogItemCommitted`:

* Kiểu Event: `com.saasovation.agilepm.domain.model.product.backlogItem.BacklogItemCommitted`
* `eventVersion`: Phiên bản số nguyên của Event, trùng khớp với phiên bản của `Notification`
* `occurredOn`: Ngày/giờ khi Event xảy ra, trùng khớp với `occurredOn` của `Notification`
* `backlogItemId`: `BacklogItemId`, chứa thuộc tính `id` dạng chuỗi văn bản
* `committedToSprintId`: `SprintId`, chứa thuộc tính `id` dạng chuỗi văn bản
* `tenantId`: `TenantId`, chứa thuộc tính `id` dạng chuỗi văn bản
* Chi tiết Event: xem các kiểu Event cụ thể

Dĩ nhiên, chúng ta sẽ đặc tả chi tiết Event cho mọi kiểu Event. Khi đã có `Notification` và tất cả các kiểu Event được đặc tả rõ ràng, chúng ta có thể sử dụng một `NotificationReader` một cách an toàn như được minh họa qua bài kiểm thử này:

```java
DomainEvent domainEvent = new TestableDomainEvent(100, "testing");
Notification notification = new Notification(1, domainEvent);
NotificationSerializer serializer = NotificationSerializer.instance();

```

```java
String serializedNotification = serializer.serialize(notification);
NotificationReader reader = new NotificationReader(serializedNotification);

assertEquals(1L, reader.notificationId());
assertEquals("1", reader.notificationIdAsString());
assertEquals(domainEvent.occurredOn(), reader.occurredOn());
assertEquals(notification.typeName(), reader.typeName());
assertEquals(notification.version(), reader.version());
assertEquals(domainEvent.eventVersion(), reader.version());

```

Bài test cho thấy cách `NotificationReader` có thể cung cấp các thành phần tiêu chuẩn đảm bảo an toàn kiểu cho mọi đối tượng `Notification` đã được tuần tự hóa.

Bài test tiếp theo cho thấy cách các thành phần đặc thù trong chi tiết của mỗi Event cũng có thể được đọc ra từ payload của `Notification`. Việc điều hướng đối tượng Event được cung cấp thông qua cú pháp tương tự XPath, hoặc các thuộc tính phân tách bằng dấu chấm, hoặc bạn có thể sử dụng các tên thuộc tính được phân tách bằng dấu phẩy (danh sách đối số biến đổi varargs của Java). Bạn có thể thấy rằng mỗi thuộc tính đều có thể được đọc dưới dạng giá trị `String` hoặc kiểu nguyên thủy (primitive) thực tế của nó (`int`, `long`, `boolean`, `double`, vân vân) nếu kiểu dữ liệu khác `String`:

```java
TestableNavigableDomainEvent domainEvent =
    new TestableNavigableDomainEvent(100, "testing");
Notification notification = new Notification(1, domainEvent);
NotificationSerializer serializer = NotificationSerializer.instance();

String serializedNotification = serializer.serialize(notification);
NotificationReader reader = new NotificationReader(serializedNotification);

assertEquals("" + domainEvent.eventVersion(), reader.eventStringValue("eventVersion"));
assertEquals("" + domainEvent.eventVersion(), reader.eventStringValue("/eventVersion"));
assertEquals(domainEvent.eventVersion(), reader.eventIntegerValue("eventVersion").intValue());
assertEquals(domainEvent.eventVersion(), reader.eventIntegerValue("/eventVersion").intValue());

assertEquals("" + domainEvent.nestedEvent().eventVersion(),
    reader.eventStringValue("nestedEvent", "eventVersion"));
assertEquals("" + domainEvent.nestedEvent().eventVersion(),
    reader.eventStringValue("/nestedEvent/eventVersion"));
assertEquals(domainEvent.nestedEvent().eventVersion(),
    reader.eventIntegerValue("nestedEvent", "eventVersion").intValue());
assertEquals(domainEvent.nestedEvent().eventVersion(),
    reader.eventIntegerValue("/nestedEvent/eventVersion").intValue());

```

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000504_7e725652c1b3475c823675ebde63e4dd41ea716dd57eb5a9fa73333dd7f0a0fb.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000505_72406629a965acf3b815941d345e1fc8c4d87ed5f94a372f031c427ac2c1085b.png)

```java
assertEquals("" + domainEvent.nestedEvent().id(),
    reader.eventStringValue("nestedEvent", "id"));
assertEquals("" + domainEvent.nestedEvent().id(),
    reader.eventStringValue("/nestedEvent/id"));
assertEquals(domainEvent.nestedEvent().id(),
    reader.eventLongValue("nestedEvent", "id").longValue());
assertEquals(domainEvent.nestedEvent().id(),
    reader.eventLongValue("/nestedEvent/id").longValue());

assertEquals("" + domainEvent.nestedEvent().name(),
    reader.eventStringValue("nestedEvent", "name"));
assertEquals("" + domainEvent.nestedEvent().name(),
    reader.eventStringValue("/nestedEvent/name"));

assertEquals("" + domainEvent.nestedEvent().occurredOn().getTime(),
    reader.eventStringValue("nestedEvent", "occurredOn"));
assertEquals("" + domainEvent.nestedEvent().occurredOn().getTime(),
    reader.eventStringValue("/nestedEvent/occurredOn"));
assertEquals(domainEvent.nestedEvent().occurredOn(),
    reader.eventDateValue("nestedEvent", "occurredOn"));
assertEquals(domainEvent.nestedEvent().occurredOn(),
    reader.eventDateValue("/nestedEvent/occurredOn"));

assertEquals("" + domainEvent.occurredOn().getTime(),
    reader.eventStringValue("occurredOn"));
assertEquals("" + domainEvent.occurredOn().getTime(),
    reader.eventStringValue("/occurredOn"));
assertEquals(domainEvent.occurredOn(),
    reader.eventDateValue("occurredOn"));
assertEquals(domainEvent.occurredOn(),
    reader.eventDateValue("/occurredOn"));

```

Lớp `TestableNavigableDomainEvent` chứa một `TestableDomainEvent`, cho phép chúng ta kiểm thử việc điều hướng tới các thuộc tính nằm sâu hơn. Các thuộc tính khác nhau được đọc ra bằng cú pháp tương tự XPath với tính năng điều hướng thuộc tính qua varargs. Chúng ta cũng kiểm thử việc đọc từng giá trị thuộc tính dưới nhiều kiểu dữ liệu khác nhau.

Vì các thể hiện `Notification` và `Event` luôn có số phiên bản (version number), bạn có thể dựa vào version để đọc các thuộc tính chuyên biệt trong một phiên bản cụ thể. Những consumer chuyên xử lý một phiên bản nhất định có thể lọc ra các phần đặc thù mà chúng cần. Tuy nhiên, các consumer cũng hoàn toàn có thể tiếp nhận bất kỳ `Notification` chứa Event nào như thể nó là phiên bản 1.

Do đó, nếu cân nhắc cẩn thận cách thiết kế từng kiểu Event, chúng ta có thể bảo vệ hầu hết các consumer khỏi sự không tương thích khi tất cả những gì chúng cần chỉ là phiên bản 1 của một Event nhất định. Những consumer như vậy sẽ không bao giờ phải thay đổi hoặc biên dịch lại khi một Event thay đổi. Tuy nhiên, bạn thực sự phải tư duy theo hướng tương thích phiên bản và lên kế hoạch cho các sửa đổi thông minh ở những phiên bản mới để không làm ảnh hưởng đến phần lớn các consumer. Đôi khi điều này là không thể đạt được, nhưng trong nhiều trường hợp, nó hoàn toàn nằm trong tầm tay.

Cách tiếp cận này có thêm ưu điểm là các Event có thể chứa nhiều hơn là chỉ các thuộc tính nguyên thủy và chuỗi văn bản. Các Event cũng có thể chứa các thể hiện của những Value Object (6) phức tạp hơn một cách an toàn, điều này đặc biệt hiệu quả khi các kiểu Value của chúng có xu hướng ổn định. Đây chắc chắn là trường hợp của `BacklogItemId`, `SprintId`, và `TenantId`, như được minh họa bởi đoạn mã sau, lần này sử dụng tính năng điều hướng thuộc tính phân tách bằng dấu chấm:

```java
NotificationReader reader = new NotificationReader(backlogItemCommittedNotification);
String backlogItemId = reader.eventStringValue("backlogItemId.id");
String sprintId = reader.eventStringValue("sprintId.id");
String tenantId = reader.eventStringValue("tenantId.id");

```

Việc bất kỳ thể hiện Value nào được chứa bên trong đều bị "đóng băng" cố định trong cấu trúc cho phép các Event không chỉ mang tính bất biến (immutable), mà còn được cố định vĩnh viễn theo thời gian. Các phiên bản mới của các kiểu Value Object nằm trong Event sẽ không ảnh hưởng đến khả năng đọc các phiên bản cũ hơn của các Value đó từ các thể hiện `Notification` đã tồn tại từ trước. Chắc chắn rằng Protocol Buffers có thể dễ sử dụng hơn nhiều khi các phiên bản Event thay đổi thường xuyên và đáng kể, và việc xử lý những thay đổi đó trở nên cồng kềnh đối với các consumer sử dụng `NotificationReader`.

Hãy hiểu rằng đây chỉ đơn thuần là một tùy chọn để xử lý giải tuần tự hóa một cách thanh thoát mà không phải deploy các kiểu Event và các dependency đi khắp mọi nơi. Một số người sẽ thấy cách tiếp cận này khá tinh tế và giải phóng họ khỏi ràng buộc, trong khi những người khác lại thấy nó mạo hiểm, vụng về, hoặc thậm chí hết sức nguy hiểm. Hướng tiếp cận ngược lại — deploy các interface và class tới mọi nơi mà các đối tượng tuần tự hóa được tiêu thụ — là điều đã quá quen thuộc. Ở đây, tôi đưa ra một số gợi ý suy ngẫm bằng cách chỉ ra một con đường ít người đi hơn.

## Cowboy Logic

* LB: "Cậu biết đấy, J, khi một gã cao bồi đã quá già để làm gương xấu, ông ta sẽ chuyển sang ban phát những lời khuyên hay."

> 💡 **Giải thích thêm:** Câu danh ngôn hài hước của cao bồi LB mượn ý từ câu châm ngôn nổi tiếng của François de La Rochefoucauld: "Người già thích đưa ra những lời khuyên hay để tự an ủi cho việc mình không còn đủ sức làm những tấm gương xấu". Tác giả Vernon tự trào rằng sau bao phen trả giá và vấp ngã với các kiến trúc phần mềm trong quá khứ, giờ đây ông đúc kết lại thành những bài học kinh nghiệm chân thực nhất cho các thế hệ kỹ sư đi sau.
> (Không có nguồn trích dẫn xác thực — cần tự kiểm chứng thêm)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000506_20361ea20e681a853f54acb8a2efd65fdd912d68a26d1abd2ea1208580eb5433.png)

Hoàn toàn có khả năng mỗi hướng tiếp cận — deploy các class để trao đổi dữ liệu tuần tự hóa so với việc định nghĩa một hợp đồng media type — đều có ưu thế riêng ở các giai đoạn khác nhau của một dự án. Ví dụ, tùy thuộc vào số lượng nhóm, số lượng Bounded Context, tần suất thay đổi, và các yếu tố khác, việc chia sẻ các class và interface có thể phát huy hiệu quả khi dự án của bạn mới bắt đầu, nhưng việc chuyển sang sử dụng hợp đồng custom media type lỏng lẻo hơn (decoupled) có thể sẽ tốt hơn ở giai đoạn production. Trong thực tế, điều này có thể phù hợp hoặc không phù hợp đối với một nhóm hoặc một tập hợp các nhóm cụ thể. Đôi khi, những gì một nhóm bắt đầu sử dụng lại chính là những gì họ gắn bó lâu dài, và họ không bao giờ dành thời gian để thực hiện một sự thay đổi 180 độ.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000507_e75df7d5f79c88386309623c7d189bd5e11faefbd02ac8078bedd2ff2e8e8c9a.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000508_a8077e07c0b57a3a80e015a5c7533372a64ff909905e5dc09edc94bb12ad68a1.png)

Để giữ cho các ví dụ xuyên suốt của chúng ta luôn đơn giản và dễ hiểu, trong phần còn lại của chương này tôi sẽ sử dụng `NotificationReader` nhất quán. Việc có sử dụng hợp đồng custom media type và `NotificationReader` trong các Bounded Context của bạn hay không hoàn toàn là quyền quyết định của bạn.

## Integration Using RESTful Resources

Khi một Bounded Context cung cấp một tập hợp phong phú các tài nguyên RESTful thông qua các URI, nó là một dạng Open Host Service (dịch vụ máy chủ mở) (3):

> Định nghĩa một giao thức cung cấp quyền truy cập vào hệ thống con của bạn dưới dạng một tập hợp các dịch vụ. Mở rộng giao thức để tất cả những ai cần tích hợp với bạn đều có thể sử dụng. Nâng cấp và mở rộng giao thức nhằm xử lý các yêu cầu tích hợp mới phát sinh. [Evans]

Chúng ta hoàn toàn có thể xem các phương thức HTTP `GET`, `PUT`, `POST`, và `DELETE` — kết hợp với các tài nguyên mà chúng thao tác — như một tập hợp các open service (dịch vụ mở). HTTP và REST chắc chắn tạo thành một giao thức mở cho phép tất cả những ai cần tích hợp với hệ thống con đều có thể thực hiện được. Việc một số lượng tài nguyên gần như không giới hạn — mỗi tài nguyên mang một định danh duy nhất thông qua một URI — có thể được tạo ra cho phép giao thức xử lý các yêu cầu tích hợp mới khi cần thiết. Đây là một phương thức rất linh hoạt cho phép các client tích hợp với Bounded Context của bạn.

Mặc dù vậy, do bên cung cấp dịch vụ RESTful phải được tương tác trực tiếp bất cứ khi nào một tài nguyên được thao tác, phong cách này không cho phép các client đạt được tính tự trị (autonomy) hoàn toàn. Nếu Bounded Context dựa trên REST trở nên không khả dụng vì một lý do nào đó, các Bounded Context client phụ thuộc sẽ không thể thực hiện các hoạt động tích hợp cần thiết trong suốt khoảng thời gian hệ thống bị gián đoạn (downtime).

Tuy nhiên, chúng ta có thể khắc phục điều này ở một mức độ nhất định bằng cách biến sự phụ thuộc vào các tài nguyên RESTful thành một rào cản nhỏ hơn đối với tính tự trị của bên tiêu thụ. Ngay cả khi RESTful (hoặc RPC) là phương tiện tích hợp duy nhất của bạn, bạn vẫn có thể tạo ra ảo giác về tính phi liên kết thời gian (temporal decoupling) bằng cách sử dụng bộ đếm thời gian (timer) hoặc messaging trong chính hệ thống của mình. Bằng cách đó, hệ thống của bạn sẽ chỉ liên hệ với bất kỳ hệ thống từ xa nào khi bộ đếm thời gian trôi qua hoặc khi nhận được một thông điệp. Nếu hệ thống từ xa không khả dụng, ngưỡng đếm thời gian có thể được lùi lại (back off), hoặc nếu sử dụng messaging, thông điệp có thể được phản hồi tiêu cực (negative acknowledge) tới broker và được phân phối lại sau. Điều này đương nhiên đặt thêm gánh nặng lên nhóm của bạn trong việc làm cho các hệ thống liên kết lỏng lẻo, nhưng đó là cái giá bạn có thể phải trả để đạt được tính tự trị.

Khi nhóm SaaSOvation phát triển Identity and Access Context cần tạo ra một phương thức để các bên tích hợp sử dụng Bounded Context của họ, họ đã xác định rằng RESTful HTTP sẽ là một trong những cách tốt nhất để mở rộng hệ thống phục vụ tích hợp mà không làm lộ trực tiếp

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000509_36dfc5ca8d8f7c13d5ed0d1f8da7d39a5a95fcbe8f8b29d4a6c0cc983a3a76ee.png)

các chi tiết cấu trúc và hành vi trong mô hình miền của họ. Đối với họ, điều này đồng nghĩa với việc thiết kế một tập hợp các tài nguyên RESTful nhằm cung cấp các biểu diễn về các khái niệm định danh (identity) và truy cập (access) theo từng tenant riêng biệt.

Phần lớn thiết kế của họ sẽ cho phép các Bounded Context tích hợp thực hiện thao tác `GET` các tài nguyên truyền tải định danh người dùng (user) và nhóm (group), đồng thời biểu thị các quyền bảo mật dựa trên vai trò (role-based security permissions) cho các kiểu định danh đó. Ví dụ, nếu một integration client cần biết liệu một người dùng trong một tenant nhất định có thể đảm nhận một vai trò truy cập cụ thể hay không, client đó sẽ thực hiện `GET` một tài nguyên bằng cách sử dụng định dạng URI sau:

`/tenants/{tenantId}/users/{username}/inRole/{role}`

Nếu người dùng của tenant đó có nắm giữ vai trò, biểu diễn tài nguyên sẽ được đưa vào phản hồi thành công `200 OK`. Ngược lại, phản hồi sẽ là mã trạng thái `204 No Content` nếu người dùng không tồn tại hoặc không nắm giữ vai trò được chỉ định. Đây là một thiết kế RESTful HTTP rất trực quan.

Hãy cùng xem cách nhóm công bố các tài nguyên truy cập và cách các integration client có thể tiêu thụ chúng theo Ubiquitous Language (1) của chính Bounded Context của họ.

## Implementing the RESTful Resource

Khi SaaSOvation bắt đầu áp dụng các nguyên lý REST vào một trong các Bounded Context của mình, họ đã rút ra được một số bài học quan trọng. Hãy cùng theo dõi hành trình của họ.

Khi nhóm SaaSOvation làm việc trong Identity and Access Context cân nhắc cách cung cấp một Open Host Service cho các bên tích hợp, ban đầu họ đã xem xét việc đơn giản là phơi bày mô hình miền của mình dưới dạng một tập hợp các tài nguyên RESTful có liên kết với nhau. Điều đó đồng nghĩa với việc cho phép các HTTP client thực hiện `GET` một tài nguyên tenant duy nhất và điều hướng xuyên suốt qua các user, group, và role của nó. Liệu đó có phải là một ý tưởng hay? Thoạt đầu nó có vẻ rất tự nhiên. Rốt cuộc, điều đó sẽ mang lại cho các client sự linh hoạt tối đa: các client có thể biết mọi thứ về mô hình miền và tự đưa ra quyết định ngay trong chính Bounded Context của mình.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000510_fa61f694303fda7703e7edb6f1ca513796eed22387f50e9dcc9fb0de4337c023.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000511_3528c564b29ddac058ba50072b358922eff4ab03934606b4c3cd3f3cec8fa3f6.png)

Pattern Context Mapping nào của DDD mô tả chính xác nhất cách tiếp cận thiết kế này? Trong thực tế, đó hoàn toàn không phải là một Open Host Service, mà tùy thuộc vào quy mô của mô hình được chia sẻ, nó sẽ là một Shared Kernel hoặc một Conformist (mô hình tuân thủ) (3). Việc phát hành một Shared Kernel hoặc chấp nhận một mối quan hệ Conformist sẽ đẩy các bên tiêu thụ vào một mối liên kết tích hợp chặt chẽ (tightly coupled) với mô hình miền được tiêu thụ. Những kiểu quan hệ đó nên tránh bằng mọi giá nếu có thể, vì chúng có xu hướng đi ngược lại những mục tiêu cơ bản nhất của DDD.

Thật may mắn là trên hành trình đó, nhóm đã tìm thấy những lời khuyên hữu ích để tránh phơi bày mô hình của mình cho client theo cách đó. Họ đã học cách tư duy dựa trên các use case (hoặc user story) mà các bên tích hợp thực sự cần. Điều đó hoàn toàn hài hòa với phần định nghĩa này của Open Host Service: "Nâng cấp và mở rộng giao thức nhằm xử lý các yêu cầu tích hợp mới phát sinh." Điều này có nghĩa là bạn chỉ cung cấp những gì các bên tích hợp cần ở hiện tại, và bạn chỉ thấu hiểu những nhu cầu đó bằng cách cân nhắc một loạt các kịch bản use case thực tế.

Khi nhóm làm theo lời khuyên đó, họ nhận ra rằng, ví dụ, điều các bên tích hợp thực sự quan tâm là liệu một người dùng nhất định có thể đảm nhận một vai trò cụ thể hay không. Việc che chắn cho các bên tích hợp khỏi các chi tiết phức tạp của mô hình miền cuối cùng sẽ giúp nâng cao năng suất của họ và làm cho các Bounded Context phụ thuộc trở nên dễ bảo trì hơn. Xét về mặt thiết kế, điều đó có nghĩa là tài nguyên RESTful `User` của họ có thể bao gồm thiết kế như sau:

```java
@Path("/tenants/{tenantId}/users")
public class UserResource {

    // ...

    @GET
    @Path("{username}/inRole/{role}")
    @Produces({ OvationsMediaType.ID_OVATION_TYPE })
    public Response getUserInRole(
            @PathParam("tenantId") String aTenantId,
            @PathParam("username") String aUsername,
            @PathParam("role") String aRoleName) {

        Response response = null;
        User user = null;

        try {
            user = this.accessService().userInRole(
                aTenantId,
                aUsername,
                aRoleName);
        } catch (Exception e) {
            // bỏ qua ngoại lệ
        }

        if (user != null) {
            response = this.userInRoleResponse(user, aRoleName);
        } else {
            response = Response.noContent().build();
        }

        return response;
    }

    // ...
}

```

Trong kiến trúc Hexagonal (4) hay Ports and Adapters (Cổng và Bộ điều hợp), lớp `UserResource` là một Adapter (Bộ điều hợp) cho RESTful HTTP Port được cung cấp bởi phần triển khai JAX-RS. Một consumer sẽ gửi một yêu cầu dưới định dạng:

```
GET /tenants/{tenantId}/users/{username}/inRole/{role}

```

Adapter sẽ ủy quyền xử lý cho `AccessService`, một Application Service (14) cung cấp API tại ranh giới hình lục giác bên trong. Là một client trực tiếp của mô hình miền, `AccessService` quản lý tác vụ use case và transaction. Tác vụ bao gồm việc tìm xem liệu `User` có tồn tại hay không, và nếu có, liệu người đó có đảm nhận vai trò được chỉ định hay không:

```java
package com.saasovation.identityaccess.application;

// ...

public class AccessService {

    // ...

    @Transactional(readOnly = true)
    public User userInRole(
            String aTenantId,
            String aUsername,
            String aRoleName) {

        User userInRole = null;
        TenantId tenantId = new TenantId(aTenantId);

        User user = DomainRegistry
            .userRepository()
            .userWithUsername(tenantId, aUsername);

        if (user != null) {
            Role role = DomainRegistry
                .roleRepository()
                .roleNamed(tenantId, aRoleName);

            if (role != null) {
                GroupMemberService groupMemberService =
                    DomainRegistry.groupMemberService();

                if (role.isInRole(user, groupMemberService)) {
                    userInRole = user;
                }
            }
        }
```

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000512_b55b07dca5999c928b94abf0ac7e286c796c4ee05e3566e2b71399102a2774eb.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000513_6945cbd271b398578411a0f345407e1f70b8ac7ae8bf567462a23eba48a01d8e.png)

```java
        return userInRole;
    }

    // ...
}

```

Application Service tìm kiếm cả Aggregate `User` lẫn Aggregate `Role` có tên tương ứng. Khi phương thức truy vấn `isInRole()` của `Role` được gọi, một `GroupMemberService` sẽ được truyền vào. Đây không phải là một Application Service, mà là một Domain Service (dịch vụ miền) (7) giúp `Role` thực hiện một số kiểm tra và truy vấn đặc thù của domain mà bản thân `Role` không nên chịu trách nhiệm.

`Response` từ `UserResource` được tạo thành từ `User` đã được phân giải cùng với tên vai trò cụ thể, sử dụng một trong các custom media type:

```java
package com.saasovation.common.media;

public class OvationsMediaType {
    public static final String COLLAB_OVATION_TYPE =
        "application/vnd.saasovation.collabovation+json";
    public static final String ID_OVATION_TYPE =
        "application/vnd.saasovation.idovation+json";
    public static final String PROJECT_OVATION_TYPE =
        "application/vnd.saasovation.projectovation+json";
    // ...
}

```

Khi người dùng nắm giữ vai trò được chỉ định, Adapter `UserResource` sẽ tạo ra một HTTP response với biểu diễn JSON có dạng như sau:

```http
HTTP/1.1 200 OK
Content-Type: application/vnd.saasovation.idovation+json
...

{
  "role": "Author",
  "username": "zoe",
  "tenantId": "A94A8298-43B8-4DA0-9917-13FFF9E116ED",
  "firstName": "Zoe",
  "lastName": "Doe",
  "emailAddress": "zoe@saasovation.com"
}

```

Như bạn sẽ thấy tiếp theo, consumer tích hợp của tài nguyên RESTful này có thể dịch nó thành kiểu đối tượng miền cụ thể mà Bounded Context của nó yêu cầu.

## Implementing the REST Client Using an Anticorruption Layer

Mặc dù biểu diễn JSON do Identity and Access Context tạo ra rất hữu ích cho các bên tích hợp, nhưng khi chúng ta tập trung vào các mục tiêu của DDD, biểu diễn này sẽ không được tiêu thụ nguyên trạng bên trong Bounded Context của client. Như đã thảo luận trong các chương trước, nếu bên tiêu thụ là Collaboration Context, nhóm phát triển sẽ không bận tâm đến các khái niệm người dùng và vai trò mang tính tổng quát, sơ khai. Thay vào đó, nhóm phát triển mô hình cộng tác chỉ quan tâm đến các vai trò đặc thù của domain. Việc ở một mô hình khác có một tập hợp các đối tượng `User` có thể được gán cho một hoặc nhiều vai trò được mô hình hóa bởi một đối tượng `Role` thực sự không nằm trong trọng tâm (sweet spot) của bối cảnh cộng tác.

Vậy làm thế nào để biến biểu diễn user-in-role này phục vụ cho các mục đích cộng tác cụ thể của chúng ta? Hãy cùng nhìn lại một Context Map đã vẽ trước đó, lần này xuất hiện trong Hình 13.1. Các thành phần quan trọng của Adapter `UserResource` đã được hiển thị trong tiểu mục trước. Phần còn lại là các interface và class cần được phát triển chuyên biệt cho Collaboration Context. Đó là `CollaboratorService`, `UserInRoleAdapter`, và `CollaboratorTranslator`. Ngoài ra còn có `HttpClient`, nhưng thành phần đó được cung cấp sẵn bởi triển khai JAX-RS thông qua các lớp `ClientRequest` và `ClientResponse`.

Hình 13.1 Open Host Service của Identity and Access Context và Anticorruption Layer của Collaboration Context được sử dụng để tích hợp giữa hai ngữ cảnh

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000514_97321952459d2dfcea1b81e48ee0555894ff95b1a681487ee74ffd44f68d8b0e.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000515_c33f0bbd075d9bb1151c266cd37576921c0807394fdf1732a4be75b92d804fe6.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000516_0e2b5f7c7140df584509d10cf3f45ad8fc985f5197a60a0835c51b999b023ae7.png)

Bộ ba gồm `CollaboratorService`, `UserInRoleAdapter`, và `CollaboratorTranslator` được sử dụng để hình thành nên một Anticorruption Layer (tầng chống làm hỏng mô hình) (3), đây là phương tiện giúp Collaboration Context tương tác với Identity and Access Context và chuyển đổi biểu diễn user-in-role thành một Value Object đại diện cho một loại `Collaborator` cụ thể.